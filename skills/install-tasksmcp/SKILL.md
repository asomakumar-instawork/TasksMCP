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

Set the `tasks-mcp` key under `mcpServers` to exactly the following, replacing `YOUR_TOKEN_HERE` with the user's token. **Overwrite any existing `tasks-mcp` entry unconditionally** — the user may have an older stdio/npx-based config that must be replaced:

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Leave all other keys in `mcpServers` untouched.

Also check whether a **project-level** `.cursor/mcp.json` exists in the current workspace. If it contains a `tasks-mcp` entry, update that file with the same config so it does not shadow the global one.

## Step 3 — Install the use-instawork skill

Write the following to `~/.cursor/skills/use-instawork/SKILL.md` (create the directory if needed):

```markdown
---
name: use-instawork
description: Dispatches a task or errand to the shared Instawork Google Sheet via the tasks-mcp server. Use when the user says "Use Instawork to...", "Log this errand", or asks to dispatch a task via Instawork.
---

# Use Instawork

## Dispatch a task

1. Call the `dispatch_task` tool with the full user request in `task_text` and `source` set to `cursor`
2. Confirm with:
   - **Task:** [task_text]
   - **Reference ID:** [client_reference_id from response]
   - **Logged at:** [timestamp from response]
   - **Status:** Finding Instawork Pro to run this errand for you

Do not show the sheet tab name or any other internal fields from the response.

## If the tool is not available

Tell the user: "The Instawork MCP isn't connected. Type 'Install TasksMCP' and I'll set it up for you."
```

## Step 4 — Confirm

Tell the user: "Done! Config written to `~/.cursor/mcp.json` and both skills installed. Restart Cursor (Cmd+Shift+P → Reload Window) to activate. Then say 'Use Instawork to …' to log a task."
