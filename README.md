# 100-Process Intelligence Engine

MODUS Enterprise AI Build Challenge — Assignment 2 submission.

An AI application that systematically analyses business processes for a
fictional retail organisation ("Kesari Retail Group"), determining
business purpose, AI opportunity, automation potential, risks, benefits,
and supporting evidence for each — for 100 seeded processes and for any
new process entered live, using the identical pipeline.

See `docs/ARCHITECTURE.md` for the full architecture, `docs/DEMO_SCRIPT.md`
for the live demo walkthrough, and `docs/SUBMISSION_CHECKLIST.md` before
you submit.

## Quick Start (Docker — recommended)

```bash
# 1. Copy env template and add your OpenAI key (or skip and use Ollama only)
cp backend/.env.example backend/.env
# edit backend/.env and set OPENAI_API_KEY=sk-...

# 2. Bring up Postgres + backend + frontend
docker compose up --build

# 3. In a second terminal, seed the 100 processes (one-time, idempotent-ish)
docker compose exec backend python ../scripts/seed_and_analyze.py
# (if running scripts from host instead, see "Local setup" below)

# 4. Open the app
# Frontend:  http://localhost:5173
# API docs:  http://localhost:8000/docs
```

## Quick Start (Local, no Docker)

Requires Python 3.11+, Node 20+, and a local PostgreSQL instance.

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL / OPENAI_API_KEY as needed
uvicorn main:app --reload

# In a new terminal: seed the data
python scripts/seed_and_analyze.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

## Using the free local model instead of OpenAI

```bash
# Install Ollama (https://ollama.com), then:
ollama pull llama3.1:8b
ollama serve
# set in backend/.env:
LLM_PROVIDER=ollama
```

No code changes needed — this is the AI provider abstraction described
in docs/ARCHITECTURE.md. If `LLM_PROVIDER=openai` but the OpenAI API is
unreachable, the app automatically falls back to Ollama if it's running.

## What to try

- **Dashboard** (`/`) — top-10 AI opportunities, human-led processes, aggregate stats
- **All Processes** (`/processes`) — sortable/filterable table of all 100+
- **Process detail** — click any process to see full analysis, evidence, and scoring breakdown
- **Add Process** (`/add`) — enter a brand-new process ("Process 101") and watch it go through
  the same pipeline live: retrieval → AI analysis → deterministic scoring → persistence

Try the canned queries directly via the API too:
```
GET /api/query/all
GET /api/query/top-ai-potential?limit=10
GET /api/query/human-led
GET /api/query/evidence/{process_name}
```

## Data model summary

`organisations` → `processes` (raw input, persisted as-is) →
`process_analysis` (versioned, AI-generated fields + code-computed
scores) → `process_evidence_links` → `evidence_sources`. Full schema in
`backend/models/models.py`. Restarting the app does not lose data —
everything lives in PostgreSQL and ChromaDB, both on persistent volumes.

## Repository structure

```
backend/     FastAPI app, AI provider abstraction, scoring, retrieval
frontend/    React SPA
data/        100-process seed dataset + research corpus
scripts/     seed_and_analyze.py — runs seed data through the real pipeline
docs/        architecture, model inventory, demo script, submission checklist
docker-compose.yml
```

## AI Tool Disclosure

_(Fill this in honestly before submitting — the brief requires it.)_

I used [tool name(s)] for [what — e.g. boilerplate generation, debugging
a specific error, code review]. I personally designed the architecture,
database schema, scoring formula, and pipeline orchestration. I
understand and can explain every component in this repository,
including [any parts you want to flag as needing more of your own review
before the live demo].

## Known limitations / honest caveats

- The research corpus in `data/research_corpus/` is currently
  **illustrative placeholder content**, not scraped from live sources —
  see `docs/RESEARCH_SOURCES.md` for why this doesn't undermine the
  architecture and how to replace it with real sources before submission.
- Query endpoints are a fixed set (not free-text-to-SQL) — a deliberate
  scope decision for reliability within the 2-day window; documented as
  a trade-off, not hidden.
- `seed_and_analyze.py` is safe to re-run but will create duplicate
  process rows if run twice without clearing the DB — fine for a fresh
  demo environment, worth knowing if you re-run it repeatedly.
