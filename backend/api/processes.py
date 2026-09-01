from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from models.models import Process, ProcessAnalysis, ProcessEvidenceLink, EvidenceSource, SourceType
from schemas.schemas import ProcessCreate, AnalysisOut, ProcessSummary, EvidenceOut
from services.analysis_pipeline import analyze_and_persist_process

router = APIRouter(prefix="/api/processes", tags=["processes"])


def _to_analysis_out(process: Process, analysis: ProcessAnalysis, db: Session) -> AnalysisOut:
    links = (
        db.query(ProcessEvidenceLink)
        .filter(ProcessEvidenceLink.analysis_id == analysis.id)
        .all()
    )
    evidence_out = []
    for link in links:
        source = db.query(EvidenceSource).get(link.source_id)
        evidence_out.append(EvidenceOut(
            title=source.title, url=source.url, source_type=source.source_type,
            snippet=link.extracted_snippet, relevance_score=float(link.relevance_score),
        ))

    return AnalysisOut(
        process_id=process.id,
        process_name=process.name,
        category=process.category,
        business_purpose=analysis.business_purpose,
        key_activities=analysis.key_activities,
        current_challenges=analysis.current_challenges,
        ai_opportunity=analysis.ai_opportunity,
        automation_potential=analysis.automation_potential.value if analysis.automation_potential else None,
        human_involvement=analysis.human_involvement,
        technologies=analysis.technologies,
        business_benefit=analysis.business_benefit,
        risks=analysis.risks,
        automation_score=float(analysis.automation_score) if analysis.automation_score is not None else None,
        priority_score=float(analysis.priority_score) if analysis.priority_score is not None else None,
        confidence=float(analysis.confidence) if analysis.confidence is not None else None,
        model_used=analysis.model_used,
        evidence=evidence_out,
    )


@router.post("", response_model=AnalysisOut)
def create_and_analyze_process(payload: ProcessCreate, db: Session = Depends(get_db)):
    """THE Process 101 endpoint. Same function seed script calls for all 100 seeds."""
    try:
        analysis = analyze_and_persist_process(
            db=db,
            org_name=payload.org_name,
            industry=payload.industry,
            process_name=payload.name,
            business_purpose_raw=payload.business_purpose_raw,
            category=payload.category,
            source_type=SourceType.user_added,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    process = db.query(Process).get(analysis.process_id)
    return _to_analysis_out(process, analysis, db)


@router.get("", response_model=list[ProcessSummary])
def list_processes(db: Session = Depends(get_db)):
    processes = db.query(Process).all()
    out = []
    for p in processes:
        latest = p.analyses[0] if p.analyses else None
        out.append(ProcessSummary(
            process_id=p.id, name=p.name, category=p.category,
            automation_potential=latest.automation_potential.value if latest and latest.automation_potential else None,
            automation_score=float(latest.automation_score) if latest and latest.automation_score is not None else None,
            priority_score=float(latest.priority_score) if latest and latest.priority_score is not None else None,
        ))
    return out


@router.get("/{process_id}", response_model=AnalysisOut)
def get_process_detail(process_id: str, db: Session = Depends(get_db)):
    process = db.query(Process).get(process_id)
    if not process or not process.analyses:
        raise HTTPException(status_code=404, detail="Process or analysis not found")
    return _to_analysis_out(process, process.analyses[0], db)
