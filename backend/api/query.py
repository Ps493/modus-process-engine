"""
Deliberately NOT free-text-to-SQL (fragile, risky, slow to build safely
in 2 days). Instead: a small set of well-defined query endpoints that
directly answer the example questions in the brief:

  "Analyse all processes."
  "Show the 10 processes with highest AI potential."
  "Which processes should remain predominantly human-led?"
  "Show me the research supporting Process 37."

Each is backed by real SQL over persisted data, not a fresh LLM call -
this is the traceable, explainable, deterministic-where-possible design
principle from the brief.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from models.models import Process, ProcessAnalysis, AutomationPotential
from schemas.schemas import ProcessSummary

router = APIRouter(prefix="/api/query", tags=["query"])


@router.get("/all", response_model=list[ProcessSummary])
def analyse_all_processes(db: Session = Depends(get_db)):
    processes = db.query(Process).all()
    out = []
    for p in processes:
        latest = p.analyses[0] if p.analyses else None
        if not latest:
            continue
        out.append(ProcessSummary(
            process_id=p.id, name=p.name, category=p.category,
            automation_potential=latest.automation_potential.value,
            automation_score=float(latest.automation_score),
            priority_score=float(latest.priority_score),
        ))
    return out


@router.get("/top-ai-potential", response_model=list[ProcessSummary])
def top_ai_potential(limit: int = 10, db: Session = Depends(get_db)):
    rows = (
        db.query(Process, ProcessAnalysis)
        .join(ProcessAnalysis, ProcessAnalysis.process_id == Process.id)
        .filter(ProcessAnalysis.version == 1)
        .order_by(ProcessAnalysis.priority_score.desc())
        .limit(limit)
        .all()
    )
    return [
        ProcessSummary(
            process_id=p.id, name=p.name, category=p.category,
            automation_potential=a.automation_potential.value,
            automation_score=float(a.automation_score),
            priority_score=float(a.priority_score),
        )
        for p, a in rows
    ]


@router.get("/human-led", response_model=list[ProcessSummary])
def human_led_processes(db: Session = Depends(get_db)):
    rows = (
        db.query(Process, ProcessAnalysis)
        .join(ProcessAnalysis, ProcessAnalysis.process_id == Process.id)
        .filter(ProcessAnalysis.version == 1)
        .filter(ProcessAnalysis.automation_potential == AutomationPotential.Low)
        .order_by(ProcessAnalysis.automation_score.asc())
        .all()
    )
    return [
        ProcessSummary(
            process_id=p.id, name=p.name, category=p.category,
            automation_potential=a.automation_potential.value,
            automation_score=float(a.automation_score),
            priority_score=float(a.priority_score),
        )
        for p, a in rows
    ]


@router.get("/evidence/{process_name}")
def evidence_for_process(process_name: str, db: Session = Depends(get_db)):
    process = db.query(Process).filter(Process.name.ilike(f"%{process_name}%")).first()
    if not process or not process.analyses:
        raise HTTPException(status_code=404, detail=f"No analysed process matching '{process_name}'")

    analysis = process.analyses[0]
    from models.models import ProcessEvidenceLink, EvidenceSource
    links = db.query(ProcessEvidenceLink).filter(ProcessEvidenceLink.analysis_id == analysis.id).all()
    evidence = []
    for link in links:
        source = db.query(EvidenceSource).get(link.source_id)
        evidence.append({
            "title": source.title, "url": source.url,
            "snippet": link.extracted_snippet, "relevance_score": float(link.relevance_score),
        })

    if not evidence:
        return {
            "process": process.name,
            "evidence": [],
            "note": "No evidence cleared the relevance threshold for this process. "
                    "The analysis is based on the process description and general model "
                    "reasoning only - treat conclusions with lower confidence.",
        }
    return {"process": process.name, "evidence": evidence}
