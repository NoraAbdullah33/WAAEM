# واءم | WAAEM — AI Governance Compliance Assistant
### ذكاء المواءمة المؤسسية · RAG compliance against official Saudi regulations

WAAEM compares any uploaded governance document (policy, procedure, manual,
internal regulation) against an **official Saudi regulatory knowledge base** using
**Retrieval-Augmented Generation (RAG)** — no hardcoded rules or manual mappings.

Upload → extract (+OCR) → clean → semantic chunk → embed → **vector-search the
official regulations** → retrieve matching requirements → **Llama** compliance
analysis (grounded strictly in retrieved chunks) → structured compliance report.

> **Real knowledge base, not mocked.** An ingestion pipeline downloads the actual
> official PDFs, extracts, chunks, embeds and indexes them into a vector database.
> Documents that can't be fetched automatically are **reported** (never faked).

## Knowledge base (Version 1)

Auto-ingested from official government portals on first startup:

| Authority | Documents | Source |
| --------- | --------- | ------ |
| **NCA** | Essential Cybersecurity Controls (ECC-2:2024) EN+AR · ECC Implementation Guide | nca.gov.sa |
| **DGA** | Digital Government Regulatory Framework · Digital Government Policies · Digital Transformation Basic Standards | dga.gov.sa |
| **NDMO** | National Data Governance Interim Regulations & Policies EN+AR | sdaia.gov.sa/ndmo |

Verified run: **8/8 official documents → 1,175 embedded chunks**. Each chunk stores
authority, document title, version, publication date, section, paragraph, chunk
text, embedding, reference id and source URL.

**Adding an authority** (MHRSD, PDPL, ISO 27001, SAMA, CST, …) requires only adding
its official documents to `app/kb/sources.py` (or a `KB_SOURCES_FILE` JSON) — no
application-logic changes.

## Architecture

```
Next.js (Vercel)  ──/api/*──►  FastAPI (Railway/Render)  ──►  PostgreSQL (metadata + history)
  upload → analyze                RAG compliance engine        Chroma (vector DB · source of truth)
  → report (AR/EN)                • ingestion: crawl → download → extract(+OCR) → chunk → embed → index
                                  • retrieval: vector search over official regulations
                                  • Llama (Ollama) compliance analysis, validated (Pydantic)
                                  └──►  Ollama (Meta Llama)
```

## Tech stack
**Frontend:** Next.js 15 · React 19 · TypeScript · Tailwind · Framer Motion · AR/EN
**Backend:** FastAPI (async) · Pydantic · SQLAlchemy 2.0 · Alembic · PostgreSQL
**RAG:** ChromaDB (vector store) · fastembed multilingual embeddings (Arabic+English) ·
pdfplumber / PyMuPDF / python-docx · pytesseract OCR · httpx crawler (robots-aware)
**AI:** Meta Llama via Ollama (retrieval-grounded scorer fallback — never invents regulations)

## REST API

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/kb/status` | KB chunks, indexed docs (provenance), ingestion failures |
| POST | `/api/kb/ingest?force=` | Run the ingestion pipeline (honest per-doc report) |
| POST | `/api/upload` | Validate + extract + store uploaded documents |
| POST | `/api/analyze` | RAG compliance analysis → `analysis_id` |
| GET | `/api/result/{id}` | Full compliance report |
| GET | `/api/report/{id}` | Flat executive report |
| GET | `/api/history` | Previous analyses |

## Compliance output
Per requirement: title · authority · source document · section · **status**
(Compliant / Partially Compliant / Non-Compliant / Not Applicable) · why · evidence
from your document · evidence from the regulation · gap analysis · recommendation ·
suggested improvement · **official citation (reference id + source URL)**. When no
evidence exists → *"Insufficient evidence found."* Every statement is backed by a
retrieved official chunk — Llama never invents regulations.

Score: overall compliance % + per-authority breakdown (DGA/NCA/NDMO) + totals
(matched / partial / missing / high-risk / critical).

## Run locally
```bash
# backend
cd backend && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
#   → on first start it auto-ingests the official Saudi regulations (needs internet;
#     the embedding model downloads once). Or trigger manually:
#     curl -X POST localhost:8000/api/kb/ingest
#     curl localhost:8000/api/kb/status

# frontend
cd frontend && npm install && cp .env.example .env.local && npm run dev   # localhost:3000
```
Enable real Meta Llama: install Ollama → `ollama pull llama3.1` (backend uses
`OLLAMA_HOST`). Without it, the retrieval-grounded scorer runs — still citing only
real retrieved regulations.

### Docker (full stack + Postgres + Ollama)
```bash
docker compose up --build          # auto-ingests the KB on first boot
docker compose exec ollama ollama pull llama3.1
```
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for Vercel + Railway/Render.

## Honest failure handling
The ingestion pipeline respects `robots.txt`, validates that downloads are real
PDFs, and records failures with reasons (WAF/bot-protection, HTTP status, broken
link, not-a-PDF, needs-OCR). Failures appear in `GET /api/kb/status` → `failures`
and in the ingestion run report. **No fabricated content, ever.**
