from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import Base, engine
from api import processes, query

# Create tables on startup if they don't exist (Alembic can take over later
# for real migrations; for a 2-day build this keeps setup to one command).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="100-Process Intelligence Engine",
    description="Enterprise AI application: retail process analysis at scale.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processes.router)
app.include_router(query.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
