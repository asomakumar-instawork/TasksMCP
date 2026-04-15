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

**Claude Desktop** does **not** accept a bare `"url"` entry (you’ll see “not valid MCP server configuration”). Use the **`mcp-remote`** bridge (**Node.js 18+** required). In **`claude_desktop_config.json`**, under **`mcpServers`**, add **`tasks-mcp`** like this (no token yet):

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

## 4. Add your token and restart

**Cursor:** edit **`tasks-mcp`** and add **`headers`**:

```json
"tasks-mcp": {
  "url": "https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp",
  "headers": {
    "Authorization": "Bearer PASTE_YOUR_TOKEN_HERE"
  }
}
```

**Claude Desktop:** keep **`command` / `args`** / **`mcp-remote`**, and add **`env`** plus a **`--header`** line (no space after **`Authorization:`** in **`args`** — Claude Desktop can mangle that; the real value lives in **`env`**):

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

Replace **`PASTE_YOUR_TOKEN_HERE`** with your token (inside **`TASKS_MCP_AUTH_HEADER`** only; keep the **`Bearer `** prefix there).

**Restart** Cursor or Claude Desktop, then ask **`dispatch_task`** again. You should get a confirmation with a **reference id** and a new row on the team sheet.

---

## Problems?

| What you see | What to try |
|----------------|-------------|
| **401** on connect | The server may still require a shared ingest secret at the gateway. Use the token your operator gave you as Bearer, or ask them to turn on **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET`**. |
| Claude says **`tasks-mcp`** config is invalid | You used **`url`** only. Switch to **`npx` + `mcp-remote`** as in step 1 (Claude Desktop). |
| Sign-in / token message from **`dispatch_task`** | Finish sign-up, add auth (**`headers`** in Cursor; **`env`** + **`--header`** in Claude), restart, retry. |
| Token message after you added a token | Token wrong, inactive in the **Tokens** sheet, or cache delay—wait ~30s, confirm status is **active**, fix typos, restart. |
| More detail | [INSTALL.md](INSTALL.md) |

Do **not** post your token in Slack, email, or a public repo.
