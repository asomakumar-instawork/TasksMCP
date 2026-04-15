# Deploy TasksMCP ingest on Google Cloud Run

This service exposes `GET /health` and `POST /v1/tasks`. The Google service account JSON should **not** be in the container image. Store it in **Secret Manager** and inject it as **`GOOGLE_SERVICE_ACCOUNT_JSON`**.

Official references: [Cloud Run quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service), [secrets as environment variables](https://cloud.google.com/run/docs/configuring/services/secrets#secret-manager).

## 0. Prereqs

- Google Cloud project with billing enabled.
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud`) installed and `gcloud auth login`.
- Your service account JSON file (Sheets API enabled; spreadsheet shared with that account’s `client_email` as Editor).
- Pick values (examples below):

| Placeholder | Example |
|-------------|---------|
| `PROJECT_ID` | `my-gcp-project` |
| `REGION` | `us-central1` |
| `SERVICE_NAME` | `tasksmcp-ingest` |

## 1. Set project and enable APIs

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="tasksmcp-ingest"

gcloud config set project "$PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

## 2. Artifact Registry (Docker repository)

```bash
gcloud artifacts repositories create tasksmcp \
  --repository-format=docker \
  --location="$REGION" \
  --description="TasksMCP images" \
  2>/dev/null || true

gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
```

## 3. Build and push the image

From the directory that contains this `Dockerfile` (`TasksMCP/backend`):

```bash
cd /path/to/TasksMCP/backend

export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/tasksmcp/${SERVICE_NAME}:v1"

gcloud builds submit --tag "$IMAGE" .
```

## 4. Store the service account key in Secret Manager

```bash
export SA_SECRET_NAME="tasksmcp-sa-json"

gcloud secrets create "$SA_SECRET_NAME" \
  --replication-policy=automatic \
  --data-file=/absolute/path/to/your-service-account.json
```

If the secret already exists, add a new version:

```bash
gcloud secrets versions add "$SA_SECRET_NAME" \
  --data-file=/absolute/path/to/your-service-account.json
```

## 5. Let Cloud Run read the secret

Cloud Run uses the **Compute Engine default service account** unless you set another. Grant it accessor on the secret:

```bash
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
export RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding "$SA_SECRET_NAME" \
  --member="serviceAccount:${RUN_SA}" \
  --role="roles/secretmanager.secretAccessor"
```

## 6. (Recommended) Ingest shared secret

So random crawlers cannot spam your sheet, set a long random string and require header `X-Tasks-Ingest-Key` on `POST /v1/tasks`.

Create a second secret (optional but recommended):

```bash
openssl rand -hex 32 | tr -d '\n' > /tmp/tasksmcp-ingest-secret.txt

gcloud secrets create tasksmcp-ingest-secret \
  --replication-policy=automatic \
  --data-file=/tmp/tasksmcp-ingest-secret.txt

gcloud secrets add-iam-policy-binding tasksmcp-ingest-secret \
  --member="serviceAccount:${RUN_SA}" \
  --role="roles/secretmanager.secretAccessor"

rm /tmp/tasksmcp-ingest-secret.txt
```

## 6b. (Optional) MCP without a token first — sign-up inside the tool

To let users add **`url` only** (no Bearer), connect once, run the **`instawork`** tool, read the onboarding text, then sign in and add their personal token:

1. Set **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true`** on the service (still keep **`TASKS_MCP_INGEST_SECRET`** if you want a shared admin key that always works as Bearer).
2. Set **`TASKS_MCP_SIGNUP_URL`** to your sign-up page (for example **`https://instawork-mcp.replit.app/get-started`**) if you still use onboarding text inside the **`instawork`** tool.
3. Keep a **`Tokens`** tab on the same spreadsheet (or set **`TASKS_MCP_TOKENS_TAB`**) with **`token`** and **`status`** columns; **`active`** means the row’s token may dispatch tasks.

Optional: **`TASKS_MCP_TOKENS_CACHE_SECONDS`** (default `30`) — how long the server caches the Tokens tab before re-reading it.

## 7. Deploy to Cloud Run

**With ingest secret (recommended):**

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --port 8080 \
  --allow-unauthenticated \
  --set-secrets="GOOGLE_SERVICE_ACCOUNT_JSON=${SA_SECRET_NAME}:latest" \
  --set-secrets="TASKS_MCP_INGEST_SECRET=tasksmcp-ingest-secret:latest" \
  --set-env-vars="TASKS_MCP_SPREADSHEET_ID=1y2rGxhmJayu1dgysUVwbc2NkkAWoXm__kpPbtT4ihUg,TASKS_MCP_SHEET_TAB=MCP outputs,TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET=true,TASKS_MCP_SIGNUP_URL=https://example.com/tasks-signup"
```

Remove **`TASKS_MCP_ALLOW_MCP_WITHOUT_INGEST_SECRET`**, **`TASKS_MCP_SIGNUP_URL`**, and trailing comma noise if you use the stricter “Bearer required to connect” mode only.

**Without ingest secret (public POST; not recommended):**

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --port 8080 \
  --allow-unauthenticated \
  --set-secrets="GOOGLE_SERVICE_ACCOUNT_JSON=${SA_SECRET_NAME}:latest" \
  --set-env-vars="TASKS_MCP_SPREADSHEET_ID=1y2rGxhmJayu1dgysUVwbc2NkkAWoXm__kpPbtT4ihUg,TASKS_MCP_SHEET_TAB=MCP outputs"
```

After deploy, note the **Service URL** (e.g. `https://tasksmcp-ingest-xxxxx-uc.a.run.app`).

- **Streamable HTTP MCP (recommended):** `{Service URL}/mcp` — clients use **`url`** + **`Authorization: Bearer <token>`** (see [INSTALL.md](../INSTALL.md)).
- **REST ingest (legacy / stdio MCP):** `{Service URL}/v1/tasks` — JSON **`POST`** with optional **`X-Tasks-Ingest-Key`**.

## 8. Verify

```bash
export URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"

curl -sS "${URL}/health"
```

Expect: `{"status":"ok"}`

Test POST (replace `TOKEN` if you set `TASKS_MCP_INGEST_SECRET`):

```bash
curl -sS -X POST "${URL}/v1/tasks" \
  -H "Content-Type: application/json" \
  -H "X-Tasks-Ingest-Key: TOKEN" \
  -d '{"task_text":"Cloud Run smoke test"}'
```

Expect JSON with `"ok": true`.

## 9. Share install steps with users

Use **[INSTALL.md](../INSTALL.md)** — installers set **`url`** to **`https://YOUR-SERVICE-URL/mcp`** and **`Authorization: Bearer`** to the same value as **`TASKS_MCP_INGEST_SECRET`** (or omit Bearer if you left the secret unset, not recommended).

## Updates

Rebuild image (step 3), then:

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION"
```
