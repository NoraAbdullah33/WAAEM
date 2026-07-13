# Deploying WAAEM to Render

This deploys the full stack on Render: **backend** (FastAPI), **frontend** (Next.js),
and a managed **PostgreSQL** database — all defined in [`render.yaml`](render.yaml).

## Prerequisites
- A [Render](https://render.com) account.
- This repo pushed to GitHub (already at `NoraAbdullah33/WAAEM`).

## 1. Create the Blueprint
1. Render Dashboard → **New +** → **Blueprint**.
2. Connect the `NoraAbdullah33/WAAEM` repository.
3. Render reads `render.yaml` and shows three resources:
   - `waaem-db` — PostgreSQL (free)
   - `waaem-backend` — Docker web service
   - `waaem-frontend` — Docker web service
4. Click **Apply**. The backend + database provision first.

## 2. Wire the frontend to the backend
The frontend proxies `/api/*` to the backend, so it needs the backend's public URL.

1. Wait for **`waaem-backend`** to finish its first deploy.
2. Copy its URL, e.g. `https://waaem-backend.onrender.com`.
3. Open **`waaem-frontend`** → **Environment** → set:
   ```
   BACKEND_URL = https://waaem-backend.onrender.com
   ```
4. Save — the frontend redeploys automatically.

Your app is then live at the **frontend** URL, e.g. `https://waaem-frontend.onrender.com`.

## 3. (Optional) Enable the LLM
The backend runs with `AI_ALLOW_FALLBACK=true`, so it works without an LLM
(canned/heuristic answers). To use a real model, point it at a hosted Ollama
endpoint:

- **`waaem-backend`** → **Environment** → set `OLLAMA_HOST` to your endpoint
  (e.g. `https://your-ollama-host:11434`), and adjust `LLAMA_MODEL` if needed.

Render does not host Ollama itself — use a separate GPU/VM host for it.

## Environment variables reference

| Service  | Variable            | Set by        | Notes |
|----------|---------------------|---------------|-------|
| backend  | `DATABASE_URL`      | Blueprint     | Auto-linked from `waaem-db`; app converts `postgres://` → asyncpg. |
| backend  | `ENVIRONMENT`       | Blueprint     | `production` |
| backend  | `CORS_ORIGINS`      | Blueprint     | `*` — tighten to the frontend URL for production. |
| backend  | `AI_ALLOW_FALLBACK` | Blueprint     | `true` |
| backend  | `OLLAMA_HOST`       | **you**       | Optional; hosted LLM endpoint. |
| frontend | `BACKEND_URL`       | **you**       | Backend public URL (step 2). |

## Notes
- Migrations run automatically on backend start (`alembic upgrade head`).
- Health check: `GET /api/health` on the backend.
- The free Postgres plan and free/starter services **sleep when idle** and expire
  after 90 days (free DB) — upgrade the plan for always-on production use.
- To tighten CORS, set `CORS_ORIGINS` on the backend to your frontend URL instead of `*`.
