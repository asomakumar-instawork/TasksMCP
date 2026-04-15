# TasksMCP — use Instawork Tasks from Claude or Cursor

After you finish the three steps below, describe your errand in normal language (place, time, what to pick up), or say something like **“Use Instawork to pick up my dry cleaning at Main Street Cleaners by Friday 5pm.”** The assistant calls the **`instawork`** tool for you. Successful runs append a row to the team Google Sheet.

---

## Step 1 — Sign up

Open:

**https://instawork-mcp.replit.app/get-started**

Follow the instructions there (for example Google sign-in) until you reach the screen that shows **your token**.

---

## Step 2 — Copy your token

Copy the token from the site and store it somewhere safe (for example a password manager). Treat it like a password.

---

## Step 3 — Add the token to your MCP config and restart

**MCP URL (same for everyone):**

`https://tasksmcp-ingest-402222098945.us-central1.run.app/mcp`

### Cursor

Edit **`.cursor/mcp.json`** (project folder or `~/.cursor/mcp.json` for all projects). Put this under **`mcpServers`** (merge with any servers you already have). Replace **`YOUR_TOKEN_HERE`** with the token from step 2 — keep the word **`Bearer`** and the space before the token.

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

**Restart Cursor** completely.

### Claude Desktop

Claude needs a small local helper (**`mcp-remote`**) because it does not support a raw **`url`** entry. You need **Node.js 18+** (so **`npx`** works).

The **`args`** below must use the public package **`mcp-remote`** (then your MCP URL). There is **no** npm package **`@instawork/tasksmcp`**; if **`npm ERR! 404 … @instawork/tasksmcp`** appears, your config was wrong—replace it with this block exactly (do not run **`npx @instawork/tasksmcp`**).

Edit **`claude_desktop_config.json`** (Claude → Settings → Developer → Edit config). Add this block **inside** **`"mcpServers"`** next to your other servers. Replace **`YOUR_TOKEN_HERE`** in **`TASKS_MCP_AUTH_HEADER`** only — the value must be **`Bearer `** then your token (one space after `Bearer`).

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
    "TASKS_MCP_AUTH_HEADER": "Bearer YOUR_TOKEN_HERE"
  }
}
```

If **`npx`** is not found when Claude starts, set **`"command"`** to the full path from running **`which npx`** in Terminal (for example **`/opt/homebrew/bin/npx`**).

**Restart Claude Desktop** completely.

---

## Run an errand

Examples you can paste into chat:

- “Use Instawork to pick up my dry cleaning at Main Street Cleaners by Friday 5pm.”
- “Log this errand: pharmacy pickup on Main St.”

If the model does not pick up the tool, you can nudge it once: “Call the **instawork** tool for that.”

You should get a confirmation that includes a **client_reference_id** and a new row on the sheet.

---

## If something fails

| Symptom | What to check |
|---------|----------------|
| **401** or MCP never connects | Token typo, token not **active** on the **Tokens** tab in the sheet, or Cloud Run env not set up for per-user tokens — ask your admin. |
| Claude: **invalid MCP server configuration** | **`tasks-mcp`** must live **inside** **`"mcpServers"`**, not next to it. |
| Claude: **could not attach** / **disconnected** | Full path to **`npx`**, Node 18+, restart Claude; see [INSTALL.md](INSTALL.md). |
| **`npm ERR! 404 … @instawork/tasksmcp`** | **`@instawork/tasksmcp` is not published.** Use **`mcp-remote`** in **`args`** as in the JSON above, not a scoped Instawork npm package. Update **get-started** copy if it still mentions **`@instawork/tasksmcp`**. |
| Tool runs but sheet does not update | Service account can edit the sheet; check Cloud Run logs. |

Do **not** paste your token in Slack, email, or a public repo.

Ready-made copies of the JSON also live in **`config-examples/`** in this repo.
