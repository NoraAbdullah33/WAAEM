# WAAEM — Deployment Guide

Two supported paths: **Docker Compose** (all-in-one) and **Render** (full stack).
DB → managed PostgreSQL; Llama → Ollama on a GPU host (or `AI_ALLOW_FALLBACK=true`).

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

## B) Render (full stack)

Render deploys the backend, frontend, and PostgreSQL together from `render.yaml`.

1. Render Dashboard → **New +** → **Blueprint** → connect the repo → **Apply**.
   This creates `waaem-db` (Postgres), `waaem-backend`, and `waaem-frontend`.
2. After the backend deploys, copy its URL and set `BACKEND_URL` on the
   **frontend** service (e.g. `https://waaem-backend.onrender.com`).
3. Optionally set `OLLAMA_HOST` on the backend (and tighten `CORS_ORIGINS`).

`DATABASE_URL` is auto-linked and normalised to `asyncpg`; migrations run on
backend boot; health check is `/api/health`. The browser calls the frontend's
own `/api/*`, which Next.js rewrites to the backend — so there are **no CORS
issues** and the API base never changes.

See **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)** for the full walkthrough.

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
