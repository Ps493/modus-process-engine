# Model & Library Inventory

## AI Models

| Component | Model | Provider | Cost | Licence | Role |
|---|---|---|---|---|---|
| Primary LLM | gpt-4o-mini | OpenAI API | Pay-per-token (free-tier credits available for new accounts) | Commercial API — usage governed by OpenAI ToS | Structures process analysis into JSON (purpose, activities, opportunity, tags) |
| Fallback LLM | llama3.1:8b | Ollama (local) | Free, runs on evaluator's own hardware | Llama 3.1 Community License (Meta) | Same role, used automatically if OpenAI is unreachable/times out |
| Embedding model | all-MiniLM-L6-v2 | sentence-transformers (local, HuggingFace) | Free | Apache 2.0 | Embeds research corpus chunks + query text for retrieval |

**What happens if OpenAI becomes unavailable/paid-tier exhausted:** the
`LLMClient` factory in `ai/llm_client.py` automatically fails over to the
local Ollama model — no code change or restart needed. If both are
unreachable, the pipeline still persists the raw process and returns a
clearly-labelled "AI analysis unavailable" result rather than fabricating
one. This is demonstrated live by stopping the `backend` container's
network access to the OpenAI API mid-demo if the evaluator wants to see it.

## Backend Libraries

| Library | Version | Licence | Purpose |
|---|---|---|---|
| FastAPI | 0.115 | MIT | Web framework / REST API |
| SQLAlchemy | 2.0 | MIT | ORM / database access |
| psycopg2-binary | 2.9 | LGPL | PostgreSQL driver |
| Alembic | 1.13 | MIT | DB migrations (scaffolded, optional for 2-day build) |
| Pydantic | 2.9 | MIT | Request/response validation |
| ChromaDB | 0.5 | Apache 2.0 | Local vector database |
| sentence-transformers | 3.2 | Apache 2.0 | Local embedding generation |
| openai | 1.51 | Apache 2.0 (client library) | OpenAI API client |
| httpx | 0.27 | BSD | HTTP client (used for Ollama calls) |
| tenacity | 9.0 | Apache 2.0 | Retry logic for LLM calls |

## Frontend Libraries

| Library | Version | Licence | Purpose |
|---|---|---|---|
| React | 18.3 | MIT | UI framework |
| React Router | 6.26 | MIT | Client-side routing |
| Vite | 5.4 | MIT | Build tool / dev server |

## Infrastructure

| Component | Licence | Notes |
|---|---|---|
| PostgreSQL 16 (Docker) | PostgreSQL License (permissive) | Primary relational store |
| Docker / Docker Compose | Apache 2.0 | Local orchestration, no cloud dependency required |

**All components are free, open-source, or free-tier**, satisfying the
brief's mandatory technology requirement. Nothing requires a paid licence
to reproduce and evaluate the solution locally.
