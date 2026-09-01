"""
Vector retrieval over the research corpus. This is what makes analysis
'grounded' rather than pure model memory: every process analysis pulls
its top-k evidence chunks from here, and the similarity score is stored
alongside the analysis so a human can audit why the AI said what it said.

If nothing clears the relevance threshold, the pipeline is told there is
no good evidence - it must not pretend otherwise.
"""
import json
import os
from functools import lru_cache

import chromadb

from config import settings
from research.embedder import embed_texts


@lru_cache(maxsize=1)
def get_chroma_collection():
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def index_corpus(corpus_dir: str):
    """Idempotent: (re)loads every .txt + matching .json metadata file in
    data/research_corpus into ChromaDB. Safe to run repeatedly."""
    collection = get_chroma_collection()
    existing_ids = set(collection.get()["ids"]) if collection.count() > 0 else set()

    ids, docs, metadatas = [], [], []
    for fname in sorted(os.listdir(corpus_dir)):
        if not fname.endswith(".txt"):
            continue
        base = fname[:-4]
        meta_path = os.path.join(corpus_dir, base + ".json")
        text_path = os.path.join(corpus_dir, fname)

        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        # naive chunking: ~800 char windows with 100 char overlap
        chunk_size, overlap = 800, 100
        start = 0
        chunk_idx = 0
        while start < len(text):
            chunk = text[start:start + chunk_size]
            chunk_id = f"{base}__chunk{chunk_idx}"
            if chunk_id not in existing_ids:
                ids.append(chunk_id)
                docs.append(chunk)
                metadatas.append({
                    "title": meta.get("title", base),
                    "url": meta.get("url", ""),
                    "source_type": meta.get("source_type", "general_web"),
                    "published_date": meta.get("published_date", ""),
                })
            start += chunk_size - overlap
            chunk_idx += 1

    if ids:
        embeddings = embed_texts(docs)
        collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)
    return len(ids)


def retrieve_evidence(query_text: str, top_k: int = None) -> list[dict]:
    """Returns list of {text, title, url, source_type, relevance_score}
    filtered to only those above settings.evidence_relevance_threshold."""
    top_k = top_k or settings.evidence_top_k
    collection = get_chroma_collection()
    if collection.count() == 0:
        return []

    query_emb = embed_texts([query_text])[0]
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)

    out = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]  # cosine distance, lower = closer

    for doc, meta, dist in zip(docs, metas, distances):
        similarity = 1 - dist  # convert distance to similarity
        if similarity < settings.evidence_relevance_threshold:
            continue
        out.append({
            "text": doc,
            "title": meta.get("title", ""),
            "url": meta.get("url", ""),
            "source_type": meta.get("source_type", ""),
            "relevance_score": round(float(similarity), 4),
        })
    return out
