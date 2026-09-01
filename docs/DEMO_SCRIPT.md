# Live Demo Script (10-15 minutes)

## 0. Setup (before the room fills, not during)
- `docker compose up --build` running, all 3 containers healthy
- `python scripts/seed_and_analyze.py` already run once, 100 processes loaded
- Browser open to `http://localhost:5173`, backend health-checked at `http://localhost:8000/api/health`

## 1. Frame the problem (30 sec)
"This is a 100-process AI intelligence engine for a fictional retail
group. It's not a script that generated 100 rows once — it's a live
pipeline. I'll prove that by having you give me a new process to analyse
in a few minutes."

## 2. Dashboard walkthrough (2 min)
- Show total processes, average automation score, human-led count
- Point at Top-10 AI Opportunity table — explain automation_score and
  priority_score are **computed by Python, not the LLM**
- Click into one process (e.g. "Demand Forecasting") — show:
  - the structured analysis (purpose, activities, challenges, opportunity)
  - the evidence panel with real similarity scores and source links
  - the scoring breakdown note explaining it's deterministic

## 3. Explain the architecture (2 min)
- Walk the diagram in `docs/ARCHITECTURE.md`
- Emphasise: LLM only produces tags/text, code computes numbers
- Emphasise: evidence comes from a vector store with a relevance
  threshold — show one process where evidence is empty and the UI
  says so explicitly rather than hiding it

## 4. THE SURPRISE RECORD TEST (4-5 min) — this is the section that matters most
- Ask the evaluator: "Give me a new process — anything in retail, or a
  process from another industry to stress-test it."
- Go to **Add Process**, type it in live
- While it's analysing, narrate what's happening server-side:
  "Right now the backend is: storing this row in Postgres, embedding the
  description, searching ChromaDB for relevant evidence, calling the LLM
  with only that evidence plus the description, then computing scores in
  Python."
- Show the result page — evidence, scores, everything populated
- Go back to Dashboard, refresh — new process appears in rankings
- **Hard-refresh the whole browser** (or restart the backend container)
  and reload the dashboard — data is still there. This proves persistence.

## 5. Answer the scaling question directly (2 min)
Read the brief's actual judging question aloud and answer it:

> "If we give your application 1,000 processes tomorrow instead of 100,
> what happens? The pipeline code doesn't change. `BackgroundTasks`
> becomes a proper queue (Celery/RQ), the analysis loop runs across
> multiple workers instead of one process, Postgres gets indexes on the
> scoring columns for fast ranking queries, and ChromaDB's HNSW index
> already scales sub-linearly. Nothing here is a single-file script that
> breaks past 100 rows — it's already list-and-loop over a real DB table."

## 6. Provider failover proof (1 min, optional if time allows)
- Show `.env` / config: `LLM_PROVIDER=openai`
- Kill network access to OpenAI (or unset the API key) and re-run one
  analysis — show it silently falls back to the local Ollama model,
  tagged in the result (`model_used: ollama:llama3.1:8b`)

## 7. Close (1 min)
- Point to README for setup reproducibility
- Point to docs/MODEL_LIBRARY_INVENTORY.md — everything free/open-source
- State clearly what you personally designed vs. where AI coding
  assistance was used (see README "AI Tool Disclosure" section)
