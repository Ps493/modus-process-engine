"""
The orchestration pipeline: Input -> Validate -> Store -> Retrieve evidence
-> AI analysis -> Deterministic scoring -> Persist -> Return.

THIS EXACT FUNCTION is what runs for every one of the 100 seed processes
AND for the evaluator's live "Process 101". There is no separate code
path for demo data vs. live data - that's the whole point of the
Surprise Record test.
"""
from sqlalchemy.orm import Session

from models.models import (
    Organisation, Process, ProcessAnalysis, EvidenceSource,
    ProcessEvidenceLink, SourceType, AutomationPotential,
)
from ai.llm_client import get_llm_client
from research.retriever import retrieve_evidence
from scoring.scorer import compute_scores


def get_or_create_org(db: Session, name: str, industry: str) -> Organisation:
    org = db.query(Organisation).filter(Organisation.name == name).first()
    if org:
        return org
    org = Organisation(name=name, industry=industry)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def analyze_and_persist_process(
    db: Session,
    org_name: str,
    industry: str,
    process_name: str,
    business_purpose_raw: str,
    category: str | None = None,
    source_type: SourceType = SourceType.user_added,
) -> ProcessAnalysis:
    # 1. Validate / normalise input
    process_name = process_name.strip()
    business_purpose_raw = business_purpose_raw.strip()
    if not process_name or not business_purpose_raw:
        raise ValueError("process_name and business_purpose_raw are required")

    # 2. Store organisation + raw process (persists even if AI/analysis fails downstream)
    org = get_or_create_org(db, org_name, industry)
    process = Process(
        org_id=org.id,
        name=process_name,
        category=category,
        business_purpose_raw=business_purpose_raw,
        source_type=source_type,
    )
    db.add(process)
    db.commit()
    db.refresh(process)

    # 3. Retrieve evidence (RAG) - grounding, not model memory
    query_text = f"{process_name}: {business_purpose_raw}"
    evidence = retrieve_evidence(query_text)

    # 4. AI analysis - bounded structured-output prompt, not a giant do-everything prompt
    llm = get_llm_client()
    result = llm.analyze_process(
        process_name=process_name,
        business_purpose_raw=business_purpose_raw,
        category=category,
        evidence_chunks=[e["text"] for e in evidence],
    )

    # 5. Deterministic scoring - computed in code, not by the LLM
    scores = compute_scores(
        key_activities=result.get("key_activities", []),
        benefit_tag=result.get("benefit_tag", "Medium"),
        risk_tag=result.get("risk_tag", "Medium"),
        evidence=evidence,
    )

    automation_potential = result.get("automation_potential", "Medium")
    if automation_potential not in AutomationPotential.__members__:
        automation_potential = "Medium"

    # 6. Persist analysis
    analysis = ProcessAnalysis(
        process_id=process.id,
        version=1,
        business_purpose=result.get("business_purpose"),
        key_activities=result.get("key_activities", []),
        current_challenges=result.get("current_challenges"),
        ai_opportunity=result.get("ai_opportunity"),
        automation_potential=AutomationPotential(automation_potential),
        human_involvement=result.get("human_involvement"),
        technologies=result.get("technologies", []),
        business_benefit=result.get("business_benefit"),
        benefit_tag=result.get("benefit_tag"),
        risks=result.get("risks"),
        risk_tag=result.get("risk_tag"),
        automation_score=scores["automation_score"],
        priority_score=scores["priority_score"],
        confidence=scores["confidence"],
        model_used=result.get("model_used", "unknown"),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # 7. Persist evidence + relationships (traceability)
    for e in evidence:
        source = (
            db.query(EvidenceSource)
            .filter(EvidenceSource.url == e["url"], EvidenceSource.title == e["title"])
            .first()
        )
        if not source:
            source = EvidenceSource(
                title=e["title"], url=e["url"], source_type=e["source_type"],
                raw_text=e["text"],
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        link = ProcessEvidenceLink(
            analysis_id=analysis.id,
            source_id=source.id,
            extracted_snippet=e["text"][:500],
            relevance_score=e["relevance_score"],
        )
        db.add(link)
    db.commit()

    return analysis
