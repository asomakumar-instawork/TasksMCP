from __future__ import annotations

import json
import os
import threading
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)

DEFAULT_SPREADSHEET_ID = "1y2rGxhmJayu1dgysUVwbc2NkkAWoXm__kpPbtT4ihUg"
DEFAULT_SHEET_TAB = "MCP outputs"
DEFAULT_SOURCE = "mcp"
DEFAULT_TOKENS_TAB = "Tokens"

_mcp_bearer_token: ContextVar[str | None] = ContextVar("mcp_bearer_token", default=None)

_tokens_cache_lock = threading.Lock()
_tokens_cache_mono: float = 0.0
_tokens_cache_active: frozenset[str] | None = None


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _effective_bearer_from_headers(headers: dict[str, str]) -> str | None:
    auth = headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        t = auth[7:].strip()
        if t:
            return t
    x = headers.get("x-tasks-ingest-key", "").strip()
    if x:
        return x
    return None


def _parse_headers(scope: dict) -> dict[str, str]:
    raw = scope.get("headers") or []
    return {k.decode().lower(): v.decode() for k, v in raw}


def _parse_active_tokens_from_rows(rows: list[list[str]]) -> frozenset[str]:
    if not rows:
        return frozenset()
    header = [str(c).strip().lower() for c in rows[0]]

    def col(name: str, default_idx: int) -> int:
        try:
            return header.index(name)
        except ValueError:
            return default_idx

    ti = col("token", 0)
    si = col("status", 5)
    hi = max(ti, si)
    out: set[str] = set()
    for row in rows[1:]:
        if len(row) <= hi:
            continue
        if str(row[si]).strip().lower() != "active":
            continue
        tok = str(row[ti]).strip()
        if tok:
            out.add(tok)
    return frozenset(out)


def _fetch_tokens_sheet_rows() -> list[list[str]]:
    spreadsheet_id = os.environ.get("TASKS_MCP_SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID).strip()
    tab = os.environ.get("TASKS_MCP_TOKENS_TAB", DEFAULT_TOKENS_TAB).strip() or DEFAULT_TOKENS_TAB
    credentials = _load_credentials()
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    escaped = tab.replace("'", "''")
    range_a1 = f"'{escaped}'!A1:Z5000"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_a1)
        .execute()
    )
    return result.get("values") or []


def _active_tokens_frozenset() -> frozenset[str]:
    global _tokens_cache_mono, _tokens_cache_active
    ttl = float(os.environ.get("TASKS_MCP_TOKENS_CACHE_SECONDS", "30"))
    now = time.monotonic()
    with _tokens_cache_lock:
        if _tokens_cache_active is not None and (now - _tokens_cache_mono) < ttl:
            return _tokens_cache_active
    rows = _fetch_tokens_sheet_rows()
    parsed = _parse_active_tokens_from_rows(rows)
    with _tokens_cache_lock:
        _tokens_cache_mono = time.monotonic()
        _tokens_cache_active = parsed
    return parsed


def _token_active_in_sheet(token: str | None) -> bool:
    if not token:
        return False
    try:
        return token in _active_tokens_frozenset()
    except Exception:
        return False


def _bearer_may_dispatch(bearer: str | None) -> bool:
    if not _env_truthy("TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET"):
        return True
    secret = os.environ.get("TASKS_MCP_INGEST_SECRET", "").strip()
    if secret and bearer == secret:
        return True
    return _token_active_in_sheet(bearer)


def _onboarding_message() -> str:
    url = os.environ.get("TASKS_MCP_SIGNUP_URL", "").strip()
    lines = [
        "You are not signed in yet, or your access token is missing, wrong, or inactive.",
        "",
    ]
    if url:
        lines.append(f"Sign in with Google here: {url}")
    else:
        lines.append("Sign in with Google using your team’s Tasks sign-up page (ask your admin for the link).")
    lines.extend(
        [
            "",
            "After you receive your token, add it to your MCP client as "
            "Authorization: Bearer <your-token> (or header X-Tasks-Ingest-Key with the same value). "
            "Then restart Cursor or Claude Desktop and run dispatch_task again.",
        ]
    )
    return "\n".join(lines)


def _require_ingest_key(x_tasks_ingest_key: str | None) -> None:
    secret = os.environ.get("TASKS_MCP_INGEST_SECRET", "").strip()
    if not secret:
        return
    if not x_tasks_ingest_key or x_tasks_ingest_key != secret:
        raise PermissionError("invalid or missing X-Tasks-Ingest-Key")


def _load_credentials():
    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw_json:
        try:
            info = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}") from e
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if creds_path:
        return service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=SCOPES,
        )

    raise RuntimeError(
        "Server misconfigured: set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS"
    )


def _append_row(values: list[str]) -> tuple[str, str]:
    spreadsheet_id = os.environ.get("TASKS_MCP_SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID).strip()
    sheet_tab = os.environ.get("TASKS_MCP_SHEET_TAB", DEFAULT_SHEET_TAB).strip()

    credentials = _load_credentials()
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    escaped = sheet_tab.replace("'", "''")
    range_a1 = f"'{escaped}'!A:D"
    body = {"values": [values]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_a1,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()
    return sheet_tab, spreadsheet_id


def _run_task(
    task_text: str,
    source: str | None,
    client_reference_id: str | None,
) -> dict:
    task_text = (task_text or "").strip()
    if not task_text:
        return {"ok": False, "error": "task_text is empty"}

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resolved_source = (source or "").strip() or DEFAULT_SOURCE
    ref = (client_reference_id or "").strip() or str(uuid.uuid4())
    row = [created, task_text, resolved_source, ref]

    try:
        sheet_tab, _ = _append_row(row)
    except FileNotFoundError:
        return {"ok": False, "error": "credentials file not found"}
    except OSError as e:
        return {"ok": False, "error": f"credentials error: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"sheets error: {e}"}

    return {
        "ok": True,
        "client_reference_id": ref,
        "created_at_utc": created,
        "sheet_tab": sheet_tab,
    }


class TaskIn(BaseModel):
    task_text: str = Field(min_length=1)
    source: str | None = None
    client_reference_id: str | None = None


mcp = FastMCP(
    "TasksMCP",
    instructions=(
        "Use dispatch_task when the user wants an errand or delivery logged to the shared task sheet. "
        "Put the full user request in task_text. After success, confirm using the tool response text. "
        "If the tool returns text about signing in or adding a token, give the user that message clearly "
        "and tell them to complete sign-in, add Authorization Bearer to MCP settings, restart the app, and retry."
    ),
    json_response=True,
    stateless_http=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
def dispatch_task(
    task_text: str,
    source: str | None = None,
    client_reference_id: str | None = None,
) -> str:
    """Record a task to the shared Google Sheet and confirm dispatch.

    Put the full user request in task_text. Optional source (e.g. claude-desktop, cursor)
    and client_reference_id for deduplication.
    """
    bearer = _mcp_bearer_token.get(None)
    if not _bearer_may_dispatch(bearer):
        return _onboarding_message()
    out = _run_task(task_text, source, client_reference_id)
    if not out.get("ok"):
        return f"Task not recorded: {out.get('error', 'unknown error')}"
    ref = out["client_reference_id"]
    created = out["created_at_utc"]
    tab = out["sheet_tab"]
    return (
        f"Task recorded and dispatched. client_reference_id: {ref}. "
        f"Logged at {created} UTC to sheet tab '{tab}'."
    )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request) -> Response:
    return JSONResponse({"status": "ok"})


@mcp.custom_route("/v1/tasks", methods=["POST"])
async def v1_tasks(request: Request) -> Response:
    try:
        key = request.headers.get("x-tasks-ingest-key")
        _require_ingest_key(key)
    except PermissionError as e:
        return JSONResponse({"detail": str(e)}, status_code=401)

    try:
        payload = await request.json()
        body = TaskIn.model_validate(payload)
    except Exception as e:
        return JSONResponse({"detail": f"invalid body: {e}"}, status_code=400)

    out = _run_task(body.task_text, body.source, body.client_reference_id)
    if not out.get("ok"):
        err = out.get("error", "unknown")
        code = 400 if "empty" in err else 502
        return JSONResponse({"detail": err}, status_code=code)
    return JSONResponse(out)


_inner = mcp.streamable_http_app()


class _McpPathAuth:
    def __init__(self, app, secret: str) -> None:
        self.app = app
        self.secret = (secret or "").strip()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or ""
        if path in ("/health", "/health/"):
            await self.app(scope, receive, send)
            return
        if path == "/v1/tasks" or path.startswith("/v1/tasks"):
            await self.app(scope, receive, send)
            return

        if path.startswith("/mcp"):
            headers = _parse_headers(scope)
            bearer = _effective_bearer_from_headers(headers)
            cv = _mcp_bearer_token.set(bearer)
            try:
                allow_anon = _env_truthy("TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET")
                ingest_header = headers.get("x-tasks-ingest-key", "")
                auth = headers.get("authorization", "")
                ok = False
                if self.secret:
                    if auth.lower().startswith("bearer "):
                        ok = auth[7:].strip() == self.secret
                    if ingest_header == self.secret:
                        ok = True
                if not self.secret or allow_anon or ok:
                    await self.app(scope, receive, send)
                else:
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 401,
                            "headers": [(b"content-type", b"application/json")],
                        }
                    )
                    await send(
                        {
                            "type": "http.response.body",
                            "body": b'{"detail":"unauthorized"}',
                        }
                    )
            finally:
                _mcp_bearer_token.reset(cv)
            return

        await self.app(scope, receive, send)


_secret = os.environ.get("TASKS_MCP_INGEST_SECRET", "").strip()
app = _McpPathAuth(_inner, _secret)
