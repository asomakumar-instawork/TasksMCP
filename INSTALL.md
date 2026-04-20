# Install Errands

Log errands to **one shared Google Sheet** from Claude, Cursor, or any MCP client that supports **Streamable HTTP** (same shape as [Doorstep](https://trydoorstep.app/docs)).

---

## Hosted MCP (recommended)

**Sign up → token → config:** **https://instawork-mcp.replit.app/get-started** → copy token → paste into the snippets below (or the files in **`config-examples/`**). Full walkthrough: **[USER_GUIDE.md](USER_GUIDE.md)**.

**MCP endpoint**

`https://errands.instawork.ai/mcp`

**Auth**

- **Personal token** from your app (row on the **`Tokens`** sheet with **`status`** = **`active`**): use **`Authorization: Bearer …`** or **`X-Tasks-Ingest-Key`**.
- **Optional** shared **`TASKS_MCP_INGEST_SECRET`** on Cloud Run: also accepted. For sheet-only tokens, set **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`** so **`/mcp`** accepts connections without the shared secret; the **`instawork`** tool still checks the **Tokens** tab. See **`backend/DEPLOY_CLOUD_RUN.md`**.

### Cursor (automated via Cursor skill)

Run one command in your terminal:

```bash
npx skills add asomakumar-instawork/TasksMCP -g -a cursor
```

Then in any Cursor chat, type: **"Install Errands"** — the agent will ask for your token and write the config automatically.

<details>
<summary>No npx / prefer curl</summary>

```bash
mkdir -p ~/.cursor/skills/install-errands ~/.cursor/skills/use-instawork && \
  curl -fsSL https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/skills/install-errands/SKILL.md \
  -o ~/.cursor/skills/install-errands/SKILL.md && \
  curl -fsSL https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/skills/use-instawork/SKILL.md \
  -o ~/.cursor/skills/use-instawork/SKILL.md
```

</details>

### Cursor (manual)

`~/.cursor/mcp.json` (global). **Restart Cursor.**

```json
{
  "mcpServers": {
    "errands": {
      "url": "https://errands.instawork.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Optional: **`Bearer ${ERRANDS_TOKEN}`** and export **`ERRANDS_TOKEN`** so the secret is not in the file.

You can use **`X-Tasks-Ingest-Key`** instead of **`Authorization`**.

### Claude Desktop

Edit **`claude_desktop_config.json`** (Claude → Settings → Developer → Edit config). Replace **`YOUR_TOKEN_HERE`** with your token. [MCP quickstart](https://modelcontextprotocol.io/quickstart/user).

```json
{
  "mcpServers": {
    "errands": {
      "url": "https://errands.instawork.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Restart Claude Desktop after edits.

### Claude Code

```bash
export ERRANDS_TOKEN="YOUR_TOKEN_HERE"
claude mcp add --transport http errands \
  https://errands.instawork.ai/mcp \
  --header "Authorization: Bearer ${ERRANDS_TOKEN}"
```

See [Claude Code MCP](https://code.claude.com/docs/en/mcp) if flags differ on your version (`claude mcp --help`).

### Try it

Ask your agent to use **Instawork** (tool name **`instawork`**) with a **`task_text`** describing the errand—for example: "Use Instawork to …". When auth succeeds, the server appends a row to the Google Sheet.

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
