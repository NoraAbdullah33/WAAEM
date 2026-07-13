# WAAEM — Deployment Guide

Three supported paths: **Docker Compose** (all-in-one), **Vercel + Railway**, and
**Vercel + Render**. Frontend → Vercel; backend → Railway/Render; DB → managed
PostgreSQL; Llama → Ollama on a GPU host (or `AI_ALLOW_FALLBACK=true`).

---

## A) Docker Compose (single host)

```bash
docker compose up --build -d
docker compose exec ollama ollama pull llama3.1     # first run only
```
- Frontend: http://localhost:3000
- Backend:  http://localhost:8000  (`/api/health`, `/api/ai/status`)
- Postgres + Ollama run as services; migrations run automatically on backend boot.

Stop: `docker compose down` (add `-v` to wipe volumes).

---

## B) Backend → Railway

1. New Project → Deploy from repo → set **root directory** to `backend`.
   Railway reads `backend/railway.json` (Dockerfile build).
2. Add a **PostgreSQL** plugin → it injects `DATABASE_URL` (auto-normalised to
   `asyncpg` by the app).
3. Set variables:
   ```
   ENVIRONMENT=production
   OLLAMA_HOST=https://<your-ollama-host>       # or leave default + AI_ALLOW_FALLBACK=true
   LLAMA_MODEL=llama3.1
   AI_ALLOW_FALLBACK=true
   CORS_ORIGINS=https://<your-vercel-domain>
   ```
4. Deploy. Start command runs `alembic upgrade head` then uvicorn on `$PORT`.

## B) Backend → Render (alternative)

- Push the repo; Render reads `render.yaml` (creates the web service + Postgres).
- Set `OLLAMA_HOST` (and optionally `CORS_ORIGINS`) in the dashboard.
- Health check: `/api/health`.

---

## C) Frontend → Vercel

1. Import the repo → set **root directory** to `frontend`.
2. Edit `frontend/vercel.json` → replace `YOUR-BACKEND-HOST` with your
   Railway/Render backend URL (this proxies `/api/*` to the backend).
   Or set env `BACKEND_URL=https://<backend-host>`.
3. Deploy. Framework preset: Next.js (auto).

The browser calls the frontend's own `/api/*`, which Vercel rewrites to the
backend — so there are **no CORS issues** and the API base never changes.

---

## D) Meta Llama (Ollama)

- **Local / Docker:** the `ollama` service; `ollama pull llama3.1`.
- **Cloud GPU:** run Ollama on a GPU VM (RunPod, Lambda, a GPU droplet), expose
  `:11434`, and point `OLLAMA_HOST` at it.
- **No GPU?** keep `AI_ALLOW_FALLBACK=true` — the platform serves the curated
  analysis and remains fully usable end-to-end.
- **llama.cpp:** set `LLAMACPP_URL=http://host:8080` for the OpenAI-compatible
  fallback path.

## Environment variables

| Variable | Default | Notes |
| -------- | ------- | ----- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./waaem.db` | Postgres in prod; `postgres://` auto-normalised |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `LLAMA_MODEL` | `llama3.1` | any pulled Llama model |
| `LLAMA_TIMEOUT` | `120` | seconds |
| `LLAMA_MAX_RETRIES` | `2` | JSON repair attempts |
| `AI_ALLOW_FALLBACK` | `true` | curated analysis when AI is unavailable |
| `LLAMACPP_URL` | *(empty)* | optional llama.cpp fallback |
| `MAX_UPLOAD_MB` | `25` | per-file limit |
| `ALLOWED_EXTENSIONS` | `pdf,docx` | accepted types |
| `CORS_ORIGINS` | `*` | comma-separated in prod |
| `BACKEND_URL` (frontend) | `http://127.0.0.1:8000` | proxy target |

## Post-deploy smoke test
```bash
curl https://<backend>/api/health          # {"status":"healthy"}
curl https://<backend>/api/ai/status        # engine availability
# upload → analyze → result
curl -F "files=@governance.pdf" https://<backend>/api/upload
```
