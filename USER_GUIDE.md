# Errands — use Instawork from Claude or Cursor

After you finish the three steps below, describe your errand in normal language (place, time, what to pick up), or say something like **"Use Instawork to pick up my dry cleaning at Main Street Cleaners by Friday 5pm."** The assistant calls the **`instawork`** tool for you. Successful runs append a row to the team Google Sheet.

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

Edit **`~/.cursor/mcp.json`** (global, applies to all projects). Put this under **`mcpServers`** (merge with any servers you already have). Replace **`YOUR_TOKEN_HERE`** with the token from step 2 — keep the word **`Bearer`** and the space before the token.

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

**Restart Cursor** completely.

### Claude Desktop

Edit **`claude_desktop_config.json`** (Claude → Settings → Developer → Edit config). Put this under **`mcpServers`** (merge with any servers you already have). Replace **`YOUR_TOKEN_HERE`** with the token from step 2 — keep the word **`Bearer`** and the space before the token.

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

**Restart Claude Desktop** completely.

---

## Run an errand

Examples you can paste into chat:

- "Use Instawork to pick up my dry cleaning at Main Street Cleaners by Friday 5pm."
- "Log this errand: pharmacy pickup on Main St."

If the model does not pick up the tool, you can nudge it once: "Call the **instawork** tool for that."

You should get a confirmation that includes a **client_reference_id** and a new row on the sheet.

---

## If something fails

| Symptom | What to check |
|---------|----------------|
| **401** or MCP never connects | Token typo, token not **active** on the **Tokens** tab in the sheet, or Cloud Run env not set up for per-user tokens — ask your admin. |
| Claude: **invalid MCP server configuration** | **`errands`** must live **inside** **`"mcpServers"`**, not next to it. |
| Claude: **could not attach** / **disconnected** | Restart Claude Desktop completely after saving the config. |
| Tool runs but sheet does not update | Service account can edit the sheet; check Cloud Run logs. |

Do **not** paste your token in Slack, email, or a public repo.

Ready-made copies of the JSON also live in **`config-examples/`** in this repo.
