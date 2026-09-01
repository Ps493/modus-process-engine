from typing import Optional, List
from pydantic import BaseModel, Field


class ProcessCreate(BaseModel):
    """What a user (or evaluator, for Process 101) submits."""
    org_name: str = Field(..., description="Organisation this process belongs to")
    industry: str = Field(..., description="Industry, e.g. Retail")
    name: str = Field(..., description="Process name, e.g. 'Demand Forecasting'")
    business_purpose_raw: str = Field(..., description="Free-text description of the process")
    category: Optional[str] = None


class EvidenceOut(BaseModel):
    title: str
    url: str
    source_type: Optional[str]
    snippet: str
    relevance_score: float

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    process_id: str
    process_name: str
    category: Optional[str]
    business_purpose: Optional[str]
    key_activities: Optional[List[str]]
    current_challenges: Optional[str]
    ai_opportunity: Optional[str]
    automation_potential: Optional[str]
    human_involvement: Optional[str]
    technologies: Optional[List[str]]
    business_benefit: Optional[str]
    risks: Optional[str]
    automation_score: Optional[float]
    priority_score: Optional[float]
    confidence: Optional[float]
    model_used: Optional[str]
    evidence: List[EvidenceOut] = []

    class Config:
        from_attributes = True


class ProcessSummary(BaseModel):
    process_id: str
    name: str
    category: Optional[str]
    automation_potential: Optional[str]
    automation_score: Optional[float]
    priority_score: Optional[float]

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    question: str
