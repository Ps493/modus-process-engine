"""
Central configuration. Everything that changes between environments
(dev laptop, evaluator's laptop, docker) comes from here / .env.
Nothing below should ever be hard-coded elsewhere in the app.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://modus:modus@localhost:5432/modus_process_engine",
    )

    # --- AI provider abstraction ---
    # "openai" or "ollama". This is the ONLY switch needed to change providers.
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))

    # --- Embeddings / vector store (always local, always free) ---
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "research_evidence")

    # Minimum similarity for evidence to be considered "grounding" a claim.
    # Below this, the system reports insufficient evidence rather than guessing.
    evidence_relevance_threshold: float = float(
        os.getenv("EVIDENCE_RELEVANCE_THRESHOLD", "0.28")
    )
    evidence_top_k: int = int(os.getenv("EVIDENCE_TOP_K", "3"))

    class Config:
        env_file = ".env"


settings = Settings()
