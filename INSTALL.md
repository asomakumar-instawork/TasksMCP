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
mkdir -p ~/.cursor/skills/install-tasksmcp ~/.cursor/skills/use-instawork && \
  curl -fsSL https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/.cursor/skills/install-tasksmcp/SKILL.md \
  -o ~/.cursor/skills/install-tasksmcp/SKILL.md && \
  curl -fsSL https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/.cursor/skills/use-instawork/SKILL.md \
  -o ~/.cursor/skills/use-instawork/SKILL.md
```

No `curl`? Use Python 3 (pre-installed on macOS):

```bash
python3 - <<'EOF'
import urllib.request, os
base = "https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/.cursor/skills"
for skill in ["install-tasksmcp", "use-instawork"]:
    path = os.path.expanduser(f"~/.cursor/skills/{skill}")
    os.makedirs(path, exist_ok=True)
    urllib.request.urlretrieve(f"{base}/{skill}/SKILL.md", f"{path}/SKILL.md")
    print(f"Installed {skill}")
EOF
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

Edit **`claude_desktop_config.json`** (Claude → Settings → Developer → Edit config). Replace **`YOUR_TOKEN_HERE`** with your token. [MCP quickstart](https://modelcontextprotocol.io/quickstart/user).

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "command": "npx",
      "args": ["instawork-mcp", "YOUR_TOKEN_HERE"]
    }
  }
}
```

Use the absolute path to **`npx`** in **`command`** if Claude cannot find it when launched from the Dock (`which npx` in Terminal).

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
| **`npm ERR! 404`** on Claude Desktop | Ensure **`args`** is **`["instawork-mcp", "YOUR_TOKEN_HERE"]`** exactly as shown above. |
