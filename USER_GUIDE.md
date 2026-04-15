# TasksMCP — quick start

Use this when you want **Claude or Cursor** to log an errand or request into Instawork’s shared task sheet.

Your server must have **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET`** enabled (see deploy docs). Otherwise you must add a Bearer token before the MCP will connect.

---

## 1. Add the MCP (URL only)

Use this **exact** MCP address:

`https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp`

**Cursor:** edit **`.cursor/mcp.json`** (project or user). Add:

```json
"tasks-mcp": {
  "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp"
}
```

**Claude Desktop** does **not** accept a bare `"url"` entry (you’ll see “not valid MCP server configuration”). Use the **`mcp-remote`** bridge (**Node.js 18+** required).

**After you redeploy** the latest backend (see below), you can start with **no** token:

```json
"tasks-mcp": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
    "--transport",
    "http-only"
  ]
}
```

**Important:** `mcp-remote` runs a **GET** on your MCP URL during discovery. The hosted server answers that probe with **200** (so OAuth does not fall through to **`POST /register`**, which used to 404). **Redeploy** the latest **`backend/`** image for that behavior.

If Claude still fails (for example Cloud Run **requires** a Bearer at the gateway), add **`--header`** + **`env`** with a token your server accepts:

```json
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
    "TASKS_MCP_AUTH_HEADER": "Bearer PASTE_YOUR_TOKEN_HERE"
  }
}
```

**Restart** Cursor or Claude Desktop.

---

## 2. Try an errand (before sign-up)

Ask for a task to be logged, for example:

- “Use **dispatch_task** to log: pick up my prescription at CVS on Main St today before 6pm.”

The assistant should run **`dispatch_task`**. The first reply will explain that you need to **sign in** and then **add your token**—follow that text.

---

## 3. Sign up and get a token

1. Open your team’s **Tasks sign-up** page (the link may appear in the MCP message, or ask your admin).
2. **Sign in with Google**.
3. When you see **your access token**, **Copy** it and store it safely (password manager). You may not see it again.

---

## 4. Add or update your token and restart

**Cursor:** if you started with **`url`** only, edit **`tasks-mcp`** and add **`headers`**:

```json
"tasks-mcp": {
  "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
  "headers": {
    "Authorization": "Bearer PASTE_YOUR_TOKEN_HERE"
  }
}
```

**Claude Desktop:** you already use **`env.TASKS_MCP_AUTH_HEADER`** in step 1. After sign-up, set that value to **`Bearer `** plus your personal token (or rotate it there). Save, **restart** Claude, then try **`dispatch_task`** again.

Replace **`PASTE_YOUR_TOKEN_HERE`** with your real token (keep the **`Bearer `** prefix in **`TASKS_MCP_AUTH_HEADER`** for Claude).

**Restart** after edits. You should get a confirmation with a **reference id** and a new row on the team sheet.

---

## Problems?

| What you see | What to try |
|----------------|-------------|
| **401** on connect | The server may still require a shared ingest secret at the gateway. Use the token your operator gave you as Bearer, or ask them to turn on **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET`**. |
| Claude says **`tasks-mcp`** config is invalid | You used **`url`** only. Switch to **`npx` + `mcp-remote`** as in step 1 (Claude Desktop). |
| Terminal: **`Not Found` is not valid JSON`** / OAuth 404 | Redeploy latest **TasksMCP** `backend` (GET `/mcp` discovery probe). If it persists, add **`--header`** + **`Bearer`** (see Claude block in step 1). |
| Sign-in / token message from **`dispatch_task`** | Finish sign-up, add auth (**`headers`** in Cursor; **`env`** + **`--header`** in Claude), restart, retry. |
| Token message after you added a token | Token wrong, inactive in the **Tokens** sheet, or cache delay—wait ~30s, confirm status is **active**, fix typos, restart. |
| More detail | [INSTALL.md](INSTALL.md) |

Do **not** post your token in Slack, email, or a public repo.
