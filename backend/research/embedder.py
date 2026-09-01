"""
Local, free embedding model. Loaded once and reused - this is what makes
retrieval free and offline-capable (no per-call API cost, no rate limit).
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer

from config import settings


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True).tolist()
