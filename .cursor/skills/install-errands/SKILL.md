---
name: install-errands
description: Installs the Errands MCP server into the user's global Cursor MCP config. Use when the user says "set up Errands", "install Errands", "add Errands MCP", or "configure Errands".
---

# Install Errands

## Step 1 — Get the token

Tell the user: "Visit https://instawork-mcp.replit.app/get-started, sign in, and paste your token here."

Wait for the token before proceeding.

## Step 2 — Write the config

**Do not treat any existing config as valid. Proceed with writing regardless of what is already in the file.**

Target file: `~/.cursor/mcp.json` (global, applies to all projects).

If the file does not exist, create it. If it exists, read it only to preserve unrelated `mcpServers` keys.

Add or overwrite the `errands` key under `mcpServers` with exactly this, substituting the user's token for `YOUR_TOKEN_HERE`:

```json
{
  "mcpServers": {
    "errands": {
      "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

**Any existing `tasks-mcp`, `tasks`, or similar entry using `"command": "npx"` or `TASKS_MCP_DIR` is the wrong package and must be replaced.** The correct config always uses `"url"`, never `"command"`.

Also check whether a **project-level** `.cursor/mcp.json` exists in the current workspace. If it contains any `tasks`-related entry, replace it with the same `errands` config above.

## Step 3 — Install the use-instawork skill

Write the following to `~/.cursor/skills/use-instawork/SKILL.md` (create the directory if needed):

```markdown
---
name: use-instawork
description: Dispatches a task or errand to the shared Instawork Google Sheet via the Errands MCP server. Use when the user says "Use Instawork to...", "Log this errand", or asks to dispatch a task via Instawork.
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

Tell the user: "The Errands MCP isn't connected. Type 'Install Errands' and I'll set it up for you."
```

## Step 4 — Confirm

Tell the user: "Done! Config written to `~/.cursor/mcp.json` and both skills installed. Restart Cursor (Cmd+Shift+P → Reload Window) to activate. Then say 'Use Instawork to …' to log a task."
