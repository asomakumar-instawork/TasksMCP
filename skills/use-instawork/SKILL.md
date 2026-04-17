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
