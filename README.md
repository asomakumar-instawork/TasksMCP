# Errands

Model Context Protocol (MCP) server that records errands in **one shared Google Sheet**.

Two ways to run it:

| Mode | Who | Credentials |
|------|-----|-------------|
| **Hosted MCP** (recommended — [Doorstep](https://trydoorstep.app/docs)-style) | You deploy **`backend/`** on Cloud Run; installers add **`url`** + **`Authorization`** in the client | Service account JSON **only on the server** |
| **Direct Sheets** | You (or trusted machines) | `GOOGLE_APPLICATION_CREDENTIALS` on that machine |

**Do not** put a service account JSON in a public repo. If everyone should write to **your** sheet, use **hosted ingest** so only your deployment holds the Google key.

## Sheet layout

Append range **A:D**. Row order:

| A | B | C | D |
|---|---|---|---|
| `created_at_utc` | `task_text` | `source` | `client_reference_id` |

## Public install (no Google key on the laptop)

1. Deploy **`backend/`** (e.g. [DEPLOY_CLOUD_RUN.md](backend/DEPLOY_CLOUD_RUN.md)) and note **`https://YOUR-SERVICE.run.app/mcp`**.
2. Set **`TASKS_MCP_INGEST_SECRET`** on the server and share that value with installers as a **Bearer token** (see [INSTALL.md](INSTALL.md)).
3. In Cursor / Claude Desktop, add an MCP server with **`url`** + **`headers.Authorization`** — same pattern as [Doorstep](https://trydoorstep.app/docs).

**Legacy:** a local **stdio** client can still **`POST /v1/tasks`** with **`TASKS_MCP_INGEST_URL`** pointing at `…/v1/tasks`; use **[INSTALL.md](INSTALL.md)** for details.

## Direct Sheets (private machine)

1. Enable **Google Sheets API**, create a **service account** + JSON key.
2. Share the spreadsheet with the service account **`client_email`** as **Editor**.

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | yes (direct mode) | Path to service account JSON |
| `TASKS_MCP_SPREADSHEET_ID` | no | Defaults to project spreadsheet id |
| `TASKS_MCP_SHEET_TAB` | no | Default `MCP outputs` |
| `TASKS_MCP_SOURCE` | no | Default `mcp` when tool omits `source` |
| `TASKS_MCP_INGEST_URL` | no | If set, **direct mode is skipped**; tasks go to this URL |
| `TASKS_MCP_INGEST_TOKEN` | no | Sent as `X-Tasks-Ingest-Key` when calling ingest |

If **`TASKS_MCP_INGEST_URL`** is set, **`GOOGLE_APPLICATION_CREDENTIALS`** is not used by the MCP process.

## MCP setup

```bash
cd TasksMCP
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
set -a && source .env && set +a
errands-mcp
```

## Deploy the ingest API (owner)

The **`backend/`** app is an ASGI service (**Streamable HTTP MCP** at **`/mcp`**, **`GET /health`**, legacy **`POST /v1/tasks`**) that holds the Google credentials and appends rows.

**Environment on the server:**

- **`GOOGLE_SERVICE_ACCOUNT_JSON`** — full JSON string (recommended on **Cloud Run** with Secret Manager; see `backend/DEPLOY_CLOUD_RUN.md`).
- **`GOOGLE_APPLICATION_CREDENTIALS`** — path to JSON file (Docker / VMs with a mounted file).
- **`TASKS_MCP_SPREADSHEET_ID`**, **`TASKS_MCP_SHEET_TAB`** — optional overrides.
- **`TASKS_MCP_INGEST_SECRET`** — optional; if set and **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET`** is not true, **`/mcp`** requires **`Authorization: Bearer …`** or **`X-Tasks-Ingest-Key`** matching this value. With **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`**, **`/mcp`** accepts connections without that header; the **`instawork`** tool then allows the same secret **or** an **active** token on the **`Tokens`** sheet tab (see `backend/DEPLOY_CLOUD_RUN.md`). **`POST /v1/tasks`** still uses **`X-Tasks-Ingest-Key`** when the secret is set.

**Google Cloud Run:** step-by-step guide: [`backend/DEPLOY_CLOUD_RUN.md`](backend/DEPLOY_CLOUD_RUN.md).

**Docker (local / VM example):**

```bash
cd backend
docker build -t errands-ingest .
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa.json \
  -v /path/on/host/sa.json:/secrets/sa.json:ro \
  -e TASKS_MCP_INGEST_SECRET=your-long-random-secret \
  errands-ingest
```

Health check: **`GET /health`**.

## Tool: `instawork` (title: Instawork)

- **`task_text`** (required)
- **`source`** (optional)
- **`client_reference_id`** (optional); UUID if omitted

## Install (Claude, Cursor, …)

Short copy-paste setup: **[INSTALL.md](INSTALL.md)** — **`url`** + **`Authorization`** (same idea as [Doorstep](https://trydoorstep.app/docs)). Claude Desktop uses **`npx mcp-remote`** + the hosted URL. Optional local **stdio** client still supported for **`/v1/tasks`**.

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
