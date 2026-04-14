from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)

DEFAULT_SPREADSHEET_ID = "1y2rGxhmJayu1dgysUVwbc2NkkAWoXm__kpPbtT4ihUg"
DEFAULT_SHEET_TAB = "MCP outputs"
DEFAULT_SOURCE = "mcp"

mcp = FastMCP(
    "TasksMCP",
    instructions=(
        "Use dispatch_task when the user wants an errand or delivery logged. "
        "After a successful call, tell the user their task is recorded and being dispatched, "
        "using the tool's returned confirmation text."
    ),
)


def _get_config() -> tuple[str, str, str]:
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS is not set. Point it at your service account JSON key file."
        )
    spreadsheet_id = os.environ.get("TASKS_MCP_SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID).strip()
    sheet_tab = os.environ.get("TASKS_MCP_SHEET_TAB", DEFAULT_SHEET_TAB).strip()
    return creds_path, spreadsheet_id, sheet_tab


def _sheets_service():
    creds_path, _, _ = _get_config()
    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def _append_row(values: list[str]) -> None:
    _, spreadsheet_id, sheet_tab = _get_config()
    escaped = sheet_tab.replace("'", "''")
    range_a1 = f"'{escaped}'!A:D"
    body = {"values": [values]}
    service = _sheets_service()
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_a1,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()


@mcp.tool()
def dispatch_task(
    task_text: str,
    source: str | None = None,
    client_reference_id: str | None = None,
) -> str:
    """Record a task as one row in Google Sheets and confirm dispatch.

    Put the full user request in task_text. Optional source labels where the task came from
    (e.g. cursor, claude); if omitted, TASKS_MCP_SOURCE env or \"mcp\" is used.
    Optional client_reference_id for deduplication; if omitted, a new id is generated.
    """
    task_text = (task_text or "").strip()
    if not task_text:
        return "No task was recorded: task_text is empty."

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resolved_source = (source or "").strip() or os.environ.get("TASKS_MCP_SOURCE", DEFAULT_SOURCE).strip()
    ref = (client_reference_id or "").strip() or str(uuid.uuid4())

    row = [created, task_text, resolved_source, ref]

    try:
        _append_row(row)
        _, _, sheet_tab = _get_config()
    except RuntimeError as e:
        return f"Task not recorded: {e}"
    except HttpError as e:
        print(f"Google Sheets API error: {e}", file=sys.stderr)
        return (
            "Task not recorded: Google Sheets returned an error. "
            "Check that the spreadsheet is shared with the service account email and that the tab name matches."
        )
    except OSError as e:
        print(f"Credentials or IO error: {e}", file=sys.stderr)
        return f"Task not recorded: could not read credentials ({e})."

    return (
        f"Task recorded and dispatched. client_reference_id: {ref}. "
        f"Logged at {created} UTC to sheet tab '{sheet_tab}' (columns: created_at_utc, task_text, source, client_reference_id)."
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
