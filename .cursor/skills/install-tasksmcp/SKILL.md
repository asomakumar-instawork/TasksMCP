---
name: install-tasksmcp
description: Installs the TasksMCP server into the user's global Cursor MCP config. Use when the user says "set up TasksMCP", "install tasks MCP", "add instawork MCP", or "configure TasksMCP".
---

# Install TasksMCP

## Step 1 — Get the token

Tell the user: "Visit https://instawork-mcp.replit.app/get-started, sign in, and paste your token here."

Wait for the token before proceeding.

## Step 2 — Write the config

Target file: `~/.cursor/mcp.json` (global, applies to all projects).

Read the file if it exists. If it doesn't exist, start with `{}`.

Merge in the following entry under `mcpServers`, replacing `<TOKEN>` with the user's token:

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN>"
      }
    }
  }
}
```

Preserve any existing `mcpServers` entries — only add or overwrite `tasks-mcp`.

## Step 3 — Confirm

Tell the user: "Config written to `~/.cursor/mcp.json`. Restart Cursor (Cmd+Shift+P → Reload Window) to activate. Then ask your agent to use the `instawork` tool to log a task."
