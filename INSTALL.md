# Install TasksMCP

Log tasks to **one shared Google Sheet** from Claude, Cursor, or any MCP client that supports **Streamable HTTP** (same shape as [Doorstep](https://trydoorstep.app/docs)).

---

## Hosted MCP URL (recommended — like Doorstep)

**MCP endpoint**

`https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp`

**Optional: URL only first, token second**

If Cloud Run has **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`** and per-user tokens live on a **`Tokens`** sheet tab, installers can add **`url`** with no **`headers`**, run **`dispatch_task`** once, read the onboarding text, then sign in and add **`Authorization: Bearer …`**. See **[USER_GUIDE.md](USER_GUIDE.md)**.

**Auth**

The server expects **`Authorization: Bearer …`** (or **`X-Tasks-Ingest-Key`**) with the value of **`TASKS_MCP_INGEST_SECRET`** on Cloud Run. Put that value in an environment variable so your config stays copy-pasteable and nothing secret lives in git.

**Instawork (GCP access)** — run once per terminal session (or add to your shell profile):

```bash
export TASKS_MCP_INGEST_BEARER="$(gcloud secrets versions access latest --secret=tasksmcp-ingest-secret --project=tasks-mcp-493318)"
```

**Everyone else** — use the same bearer string your admin shares (e.g. 1Password); set **`TASKS_MCP_INGEST_BEARER`** to that value before starting the client.

Clients that expand **`${…}`** from the environment (Cursor does; Claude Desktop usually does when launched from a shell that has the variable) can use the snippets below as-is.

### Cursor

`.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global). **Restart Cursor.**

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer ${TASKS_MCP_INGEST_BEARER}"
      }
    }
  }
}
```

You can use **`X-Tasks-Ingest-Key`** instead of **`Authorization`** if your client prefers:

```json
"headers": {
  "X-Tasks-Ingest-Key": "${TASKS_MCP_INGEST_BEARER}"
}
```

### Claude Desktop

`claude_desktop_config.json` ([paths](https://docs.claude.com/en/docs/claude-desktop/mcp)):

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer ${TASKS_MCP_INGEST_BEARER}"
      }
    }
  }
}
```

Restart Claude Desktop. If **`${TASKS_MCP_INGEST_BEARER}`** is not expanded, paste the raw token after **`Bearer `** in that file (keep the file private).

### Claude Code

```bash
claude mcp add --transport http tasks-mcp \
  https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp \
  --header "Authorization: Bearer ${TASKS_MCP_INGEST_BEARER}"
```

See [Claude Code MCP](https://code.claude.com/docs/en/mcp) if flags differ on your version (`claude mcp --help`).

### Try it

Ask your agent to call **`dispatch_task`** with a **`task_text`** describing the task.

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
| 401 on MCP | Token must match **`TASKS_MCP_INGEST_SECRET`**; header **`Authorization: Bearer …`** or **`X-Tasks-Ingest-Key`**. Re-run the **`export`** or refresh the value from your admin. |
| Client does not support `url` + Streamable HTTP | Use the stdio + **`/v1/tasks`** flow in the README, or upgrade the client. |
| Tasks not appearing | Sheet must be shared with the service account; check Cloud Run logs. |
