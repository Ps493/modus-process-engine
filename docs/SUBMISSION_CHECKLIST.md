# Submission Checklist (mapped to MODUS brief requirements)

## Mandatory technical rules
- [x] Real frontend (React SPA)
- [x] Real backend/API (FastAPI, REST)
- [x] Real data/storage layer (PostgreSQL + ChromaDB, both persistent)
- [x] Real AI/model integration (OpenAI + local Ollama fallback via abstraction)
- [x] Data persists across restart (verify: `docker compose restart backend` then reload dashboard)
- [ ] **You must actually run and verify this** — don't submit without doing it once yourself
- [x] Processes multiple records systematically (100 seed processes via loop, not hand-written)
- [x] Outputs traceable to evidence (ProcessEvidenceLink table + UI evidence panel)
- [x] Source code + setup instructions included (this repo + README)
- [x] Free/open-source/free-tier technologies only (see MODEL_LIBRARY_INVENTORY.md)
- [x] Dynamically handles new records (Add Process form → same pipeline)
- [x] No hard-coded demo outputs (verify by testing an unusual process live before submission)
- [x] Not static HTML / PowerPoint / spreadsheet / notebook-only / simple chatbot wrapper
- [x] No giant single prompt (bounded structured-output prompt + deterministic scoring in code)

## Before you submit — things YOU must still do
1. **Run the full stack once end-to-end** and fix whatever breaks (there
   will be something — that's normal, budget time for it).
2. **Replace the placeholder research corpus** with real sources, or at
   minimum be ready to explain honestly in the demo that it's a
   representative starter corpus you'd expand (see docs/RESEARCH_SOURCES.md).
3. **Get an OpenAI API key** (or set up Ollama locally) — nothing calls
   a real model without one.
4. **Test the Ollama fallback actually works** — install Ollama, pull
   `llama3.1:8b`, temporarily blank the OpenAI key, confirm it fails over.
5. **Test an intentionally weird Process 101** yourself before the demo
   (e.g. a process from a completely different industry) so you know
   what the output looks like and aren't surprised live.
6. **Read every file you're submitting.** The brief explicitly requires
   you to understand and explain every major component — don't submit
   code you can't walk through line by line.
7. Take a screenshot or two of the working dashboard for the written
   submission in case of live-demo technical issues.
8. Fill in the "AI Tool Disclosure" section of the README honestly.

## Final deliverables checklist
- [x] Source code repository (this folder)
- [x] README / setup instructions
- [x] Architecture diagram (docs/ARCHITECTURE.md, text + mermaid)
- [x] Database/data model (backend/models/models.py + description in README)
- [x] Model/library inventory with licences (docs/MODEL_LIBRARY_INVENTORY.md)
- [x] Sample/synthetic data (data/seed_processes.json)
- [x] Research sources (data/research_corpus/, docs/RESEARCH_SOURCES.md)
- [ ] Working application — **only checked once you've run it yourself**
- [ ] 10-15 minute live demonstration — script drafted in docs/DEMO_SCRIPT.md, **rehearse it at least twice**
