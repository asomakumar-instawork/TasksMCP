# TasksMCP

Model Context Protocol (MCP) server that appends one row per task to Google Sheets and returns a short confirmation.

## Sheet layout

Append range **A:D** on the configured tab. Row order:

| A | B | C | D |
|---|---|---|---|
| `created_at_utc` | `task_text` | `source` | `client_reference_id` |

Put a header row in the sheet with those names; the server only appends data rows.

## Google setup

1. Enable **Google Sheets API** and create a **service account** with a **JSON** key in Google Cloud Console.
2. Share the spreadsheet with the service account **`client_email`** (from the JSON) as **Editor**.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | yes | Absolute path to the service account JSON key |
| `TASKS_MCP_SPREADSHEET_ID` | no | Defaults to the TasksMCP spreadsheet id |
| `TASKS_MCP_SHEET_TAB` | no | Default `MCP outputs` |
| `TASKS_MCP_SOURCE` | no | Default `mcp`; used when `dispatch_task` is called without `source` |

## Setup

```bash
cd TasksMCP
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run (stdio)

```bash
set -a && source .env && set +a
tasks-mcp
```

## Cursor `mcp.json` example

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "command": "/absolute/path/to/TasksMCP/.venv/bin/tasks-mcp",
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/absolute/path/to/service-account.json",
        "TASKS_MCP_SPREADSHEET_ID": "1y2rGxhmJayu1dgysUVwbc2NkkAWoXm__kpPbtT4ihUg",
        "TASKS_MCP_SHEET_TAB": "MCP outputs",
        "TASKS_MCP_SOURCE": "cursor"
      }
    }
  }
}
```

## Tool: `dispatch_task`

- **`task_text`** (required): full task description in one string.
- **`source`** (optional): overrides `TASKS_MCP_SOURCE` for that row.
- **`client_reference_id`** (optional): your id for deduplication; if omitted, a UUID is written.

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
