# Install TasksMCP

Log tasks to **one shared Google Sheet** from Claude, Cursor, or any MCP client that supports **Streamable HTTP** (same shape as [Doorstep](https://trydoorstep.app/docs)).

---

## Hosted MCP (recommended)

**Sign up → token → config:** **https://instawork-mcp.replit.app/get-started** → copy token → paste into the snippets below (or the files in **`config-examples/`**). Full walkthrough: **[USER_GUIDE.md](USER_GUIDE.md)**.

**MCP endpoint**

`https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp`

**Auth**

- **Personal token** from your app (row on the **`Tokens`** sheet with **`status`** = **`active`**): use **`Authorization: Bearer …`** or **`X-Tasks-Ingest-Key`**.
- **Optional** shared **`TASKS_MCP_INGEST_SECRET`** on Cloud Run: also accepted. For sheet-only tokens, set **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`** so **`/mcp`** accepts connections without the shared secret; the **`instawork`** tool still checks the **Tokens** tab. See **`backend/DEPLOY_CLOUD_RUN.md`**.

### Cursor (automated via Cursor skill)

Let the agent handle the setup for you. Run this once in your terminal to install the skill:

```bash
mkdir -p ~/.cursor/skills/install-tasksmcp && \
  curl -fsSL https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/.cursor/skills/install-tasksmcp/SKILL.md \
  -o ~/.cursor/skills/install-tasksmcp/SKILL.md
```

Then in any Cursor chat, type: **"Install TasksMCP"** — the agent will ask for your token and write the config automatically.

### Cursor (manual)

`~/.cursor/mcp.json` (global). **Restart Cursor.**

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

Optional: **`Bearer ${TASKS_MCP_TOKEN}`** and export **`TASKS_MCP_TOKEN`** so the secret is not in the file.

You can use **`X-Tasks-Ingest-Key`** instead of **`Authorization`**.

### Claude Desktop

`claude_desktop_config.json` only supports **`command`**-based servers. Use **`npx`** + **`mcp-remote`** and **`--transport http-only`**. Put the token in **`env`** so the **`Authorization:`** line is not split inside **`args`**. [MCP quickstart](https://modelcontextprotocol.io/quickstart/user).

**Do not** use **`npx @instawork/tasksmcp`** (or **`command`**: **`@instawork/tasksmcp`**): that package is **not** on the public npm registry. **`404 Not Found … @instawork/tasksmcp`** means the config should use **`mcp-remote`** and the hosted URL below, like the JSON snippet.

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
        "--transport",
        "http-only",
        "--header",
        "Authorization:${TASKS_MCP_AUTH_HEADER}"
      ],
      "env": {
        "TASKS_MCP_AUTH_HEADER": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Use the absolute path to **`npx`** in **`command`** if Claude cannot find it when launched from the Dock.

Restart Claude Desktop after edits.

### Claude Code

```bash
export TASKS_MCP_TOKEN="YOUR_TOKEN_HERE"
claude mcp add --transport http tasks-mcp \
  https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp \
  --header "Authorization: Bearer ${TASKS_MCP_TOKEN}"
```

See [Claude Code MCP](https://code.claude.com/docs/en/mcp) if flags differ on your version (`claude mcp --help`).

### Try it

Ask your agent to use **Instawork** (tool name **`instawork`**) with a **`task_text`** describing the task—for example: “Use Instawork to …”. When auth succeeds, the server appends a row to the Google Sheet.

---

## If the server has **no** ingest secret

If **`TASKS_MCP_INGEST_SECRET`** is not set on Cloud Run, **`/mcp`** does not require a token (fine for experiments; **not** recommended for production).

---

## Legacy: local stdio MCP + `POST /v1/tasks`

Some setups run a **Python process** on the laptop that POSTs JSON to **`https://…/v1/tasks`**. That still works for backward compatibility; see **[README.md](README.md)** (`TASKS_MCP_INGEST_URL` pointing at **`/v1/tasks`**, not **`/mcp`**). You do **not** need this if you use the **`url`** config above.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 on MCP | Use the token from **get-started** (or **`TASKS_MCP_INGEST_SECRET`** if your deploy uses it); **`status`** on **`Tokens`** must be **`active`**; header **`Authorization: Bearer …`** or **`X-Tasks-Ingest-Key`**. |
| Client does not support `url` + Streamable HTTP | Use the stdio + **`/v1/tasks`** flow in the README, or upgrade the client. |
| Tasks not appearing | Sheet must be shared with the service account; check Cloud Run logs. |
| **`npm ERR! 404 … @instawork/tasksmcp`** | Use **`mcp-remote`** in **`args`**, not **`@instawork/tasksmcp`**. Align **get-started** / internal docs with **`config-examples/claude-desktop.tasks-mcp.json`**. |
