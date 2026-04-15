# Install TasksMCP

Log tasks to **one shared Google Sheet** from Claude, Cursor, or any MCP client that supports **Streamable HTTP** (same shape as [Doorstep](https://trydoorstep.app/docs)).

---

## Hosted MCP URL (recommended — like Doorstep)

**MCP endpoint**

`https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp`

**Optional: URL only first, token second**

If Cloud Run has **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`** and per-user tokens live on a **`Tokens`** sheet tab, installers can connect without a Bearer first, run **`dispatch_task`** once, read the onboarding text, then sign in and add auth. **Cursor:** **`url`** only, then **`headers`**. **Claude Desktop:** use **`mcp-remote`** with a **Bearer** in **`--header`** / **`env`** from the start (see below)—**`mcp-remote` without a header** often errors on OAuth discovery **404**. See **[USER_GUIDE.md](USER_GUIDE.md)**.

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

`claude_desktop_config.json` only loads servers that start with **`command`** (stdio). For a hosted **Streamable HTTP** MCP, use **`npx`** + **`mcp-remote`** ([npm](https://www.npmjs.com/package/mcp-remote)) and **`--transport http-only`**. Paths: [MCP quickstart](https://modelcontextprotocol.io/quickstart/user).

**OAuth vs `mcp-remote`:** The bridge **GET**s the MCP URL first. TasksMCP returns **200** for that discovery-style GET (no **`mcp-protocol-version`** / session headers) so **`mcp-remote` does not** fall through to **`POST /register`** on your origin (which used to 404). **Redeploy** the current **`backend/`** image. If the gateway still requires a Bearer for **POST** `/mcp`, keep **`--header`** + **`env`** as below.

**With Bearer token** (put the token in **`env`** so spaces in `Authorization: Bearer …` are not broken inside **`args`**):

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
        "TASKS_MCP_AUTH_HEADER": "Bearer ${TASKS_MCP_INGEST_BEARER}"
      }
    }
  }
}
```

Export **`TASKS_MCP_INGEST_BEARER`** before launching Claude Desktop, or replace **`${TASKS_MCP_INGEST_BEARER}`** with the raw token inside **`TASKS_MCP_AUTH_HEADER`** (keep the file private).

**Claude Desktop + `mcp-remote` without a Bearer header** is unreliable against TasksMCP (OAuth probe hits **404**). Prefer **`url`**-only first on **Cursor** if you want that flow; on Claude, include **`--header`** + **`env`** from the start.

Restart Claude Desktop after edits.

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
