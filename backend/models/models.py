"""
Persistent schema.

Design principle (per challenge brief): the ORIGINAL input and the
GENERATED analysis are separate, versioned tables. Refreshing/restarting
the app never destroys intelligence because everything here is committed
to Postgres, not held in memory.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Numeric, DateTime, ForeignKey,
    Enum as SAEnum, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class SourceType(str, enum.Enum):
    seed = "seed"
    user_added = "user_added"


class AutomationPotential(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class Organisation(Base):
    __tablename__ = "organisations"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    processes = relationship("Process", back_populates="organisation")


class Process(Base):
    __tablename__ = "processes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organisations.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    business_purpose_raw = Column(Text, nullable=False)  # exactly what was submitted
    source_type = Column(SAEnum(SourceType), default=SourceType.seed)
    created_at = Column(DateTime, default=datetime.utcnow)

    organisation = relationship("Organisation", back_populates="processes")
    analyses = relationship("ProcessAnalysis", back_populates="process", order_by="desc(ProcessAnalysis.version)")


class ProcessAnalysis(Base):
    __tablename__ = "process_analysis"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    process_id = Column(UUID(as_uuid=False), ForeignKey("processes.id"), nullable=False)
    version = Column(Integer, default=1)

    business_purpose = Column(Text)
    key_activities = Column(ARRAY(String))
    current_challenges = Column(Text)
    ai_opportunity = Column(Text)
    automation_potential = Column(SAEnum(AutomationPotential))
    human_involvement = Column(Text)
    technologies = Column(ARRAY(String))
    business_benefit = Column(Text)
    benefit_tag = Column(String)   # Low/Medium/High, used in scoring
    risks = Column(Text)
    risk_tag = Column(String)      # Low/Medium/High, used in scoring

    automation_score = Column(Numeric)   # deterministic, computed in scoring/scorer.py
    priority_score = Column(Numeric)     # deterministic, computed in scoring/scorer.py
    confidence = Column(Numeric)         # evidence-coverage based, computed in code

    model_used = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)

    process = relationship("Process", back_populates="analyses")
    evidence_links = relationship("ProcessEvidenceLink", back_populates="analysis")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source_type = Column(String)          # e.g. "industry_report", "vendor", "general_web"
    published_date = Column(String, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text)

    links = relationship("ProcessEvidenceLink", back_populates="source")


class ProcessEvidenceLink(Base):
    __tablename__ = "process_evidence_links"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    analysis_id = Column(UUID(as_uuid=False), ForeignKey("process_analysis.id"), nullable=False)
    source_id = Column(UUID(as_uuid=False), ForeignKey("evidence_sources.id"), nullable=False)
    extracted_snippet = Column(Text)
    relevance_score = Column(Numeric)  # cosine similarity at retrieval time

    analysis = relationship("ProcessAnalysis", back_populates="evidence_links")
    source = relationship("EvidenceSource", back_populates="links")


class QueryLog(Base):
    __tablename__ = "query_log"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
