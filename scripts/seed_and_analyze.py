"""
Run this once after the stack is up:  python scripts/seed_and_analyze.py

What it does:
1. Indexes data/research_corpus into ChromaDB (idempotent).
2. Loads data/seed_processes.json (100 processes).
3. Calls the SAME analyze_and_persist_process() function that the live
   "/api/processes" POST endpoint calls for the evaluator's Process 101.

This is the proof point that the 100 seed rows are not hand-written
outputs - they are produced by the pipeline, one call at a time, with a
small delay to be gentle on rate limits.
"""
import json
import os
import sys
import time

_here = os.path.dirname(__file__)
for _candidate in (
    os.path.join(_here, "..", "backend"),  # host layout
    os.path.join(_here, ".."),             # docker layout
):
    if os.path.exists(os.path.join(_candidate, "config.py")):
        sys.path.insert(0, _candidate)
        break
else:
    raise RuntimeError(
        "Could not locate backend/config.py from either expected location. "
        "Run this script from the project root, or inside the backend container."
    )

from database.session import SessionLocal, Base, engine  # noqa: E402
from services.analysis_pipeline import analyze_and_persist_process  # noqa: E402
from models.models import SourceType  # noqa: E402
from research.retriever import index_corpus  # noqa: E402

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "research_corpus")
SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "seed_processes.json")


def main():
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)

    print("Indexing research corpus into ChromaDB...")
    n_chunks = index_corpus(CORPUS_DIR)
    print(f"  -> {n_chunks} new chunks indexed")

    with open(SEED_FILE) as f:
        seed = json.load(f)

    db = SessionLocal()
    total = len(seed["processes"])
    print(f"Analysing {total} seed processes through the live pipeline...")

    ok, failed = 0, []
    for i, p in enumerate(seed["processes"], start=1):
        try:
            analyze_and_persist_process(
                db=db,
                org_name=seed["org_name"],
                industry=seed["industry"],
                process_name=p["name"],
                business_purpose_raw=p["business_purpose_raw"],
                category=p["category"],
                source_type=SourceType.seed,
            )
            ok += 1
            print(f"  [{i}/{total}] OK - {p['name']}")
        except Exception as e:
            failed.append((p["name"], str(e)))
            print(f"  [{i}/{total}] FAILED - {p['name']}: {e}")
        time.sleep(0.3)  # be gentle on API rate limits

    db.close()
    print(f"\nDone. {ok} succeeded, {len(failed)} failed.")
    if failed:
        print("Failed processes (re-run script to retry - it's safe, "
              "each process creates a new row but won't duplicate evidence sources):")
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
