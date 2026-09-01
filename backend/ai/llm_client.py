"""
AI service abstraction.

This is the single interface every provider must implement. The rest of
the application (services/analysis_pipeline.py) only ever talks to this
interface, never to OpenAI or Ollama directly. Swapping providers, or
adding a new one, means writing one new class here - nothing else in the
codebase changes.
"""
from abc import ABC, abstractmethod
from typing import Optional


ANALYSIS_JSON_SCHEMA_HINT = """
Return ONLY valid JSON with exactly these keys:
{
  "business_purpose": "string, why this process exists",
  "key_activities": ["short phrase", "short phrase", ...],
  "current_challenges": "string, 1-3 sentences",
  "ai_opportunity": "string, 1-3 sentences on how AI could change this process",
  "automation_potential": "Low" | "Medium" | "High",
  "human_involvement": "string, what stays human and why",
  "technologies": ["e.g. NLP", "e.g. forecasting models", ...],
  "business_benefit": "string, 1-2 sentences",
  "benefit_tag": "Low" | "Medium" | "High",
  "risks": "string, 1-2 sentences on AI/operational/regulatory risk",
  "risk_tag": "Low" | "Medium" | "High",
  "confidence": 0.0 to 1.0 (your own confidence in this analysis given the evidence provided)
}
No prose outside the JSON. No markdown fences.
"""


def build_prompt(process_name: str, business_purpose_raw: str,
                  category: Optional[str], evidence_chunks: list[str]) -> str:
    evidence_block = "\n\n".join(
        f"[Evidence {i+1}]: {chunk}" for i, chunk in enumerate(evidence_chunks)
    ) if evidence_chunks else "No directly relevant evidence was retrieved for this process."

    return f"""You are analysing ONE specific business process for an enterprise AI opportunity assessment.

Process name: {process_name}
Category: {category or "unspecified"}
Description provided: {business_purpose_raw}

Supporting research evidence (use this to ground your analysis; if it does not
cover something, say so plainly rather than inventing specifics):
{evidence_block}

{ANALYSIS_JSON_SCHEMA_HINT}
"""


class LLMClient(ABC):
    @abstractmethod
    def analyze_process(self, process_name: str, business_purpose_raw: str,
                         category: Optional[str], evidence_chunks: list[str]) -> dict:
        """Returns a dict matching the schema in ANALYSIS_JSON_SCHEMA_HINT,
        plus a 'model_used' key identifying which model produced it."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError


def get_llm_client() -> LLMClient:
    """Factory - reads config.settings.llm_provider and returns the right client.
    Falls back to Ollama automatically if the configured provider is unreachable,
    satisfying the 'external AI provider failure' requirement."""
    from config import settings
    from ai.openai_client import OpenAIClient
    from ai.ollama_client import OllamaClient

    primary = OpenAIClient() if settings.llm_provider == "openai" else OllamaClient()
    fallback = OllamaClient() if settings.llm_provider == "openai" else OpenAIClient()

    class FailoverClient(LLMClient):
        def analyze_process(self, *args, **kwargs) -> dict:
            if primary.is_available():
                try:
                    return primary.analyze_process(*args, **kwargs)
                except Exception:
                    pass  # fall through to fallback
            if fallback.is_available():
                result = fallback.analyze_process(*args, **kwargs)
                result["fallback_used"] = True
                return result
            # Both providers unavailable - degrade gracefully, do not fabricate.
            return {
                "business_purpose": business_purpose_raw_safe(kwargs, args),
                "key_activities": [],
                "current_challenges": "AI analysis unavailable: no LLM provider reachable.",
                "ai_opportunity": "Unavailable - please retry once a model provider is reachable.",
                "automation_potential": "Medium",
                "human_involvement": "Unavailable",
                "technologies": [],
                "business_benefit": "Unavailable",
                "benefit_tag": "Medium",
                "risks": "Unavailable",
                "risk_tag": "Medium",
                "confidence": 0.0,
                "model_used": "none-degraded",
            }

        def is_available(self) -> bool:
            return primary.is_available() or fallback.is_available()

    return FailoverClient()


def business_purpose_raw_safe(kwargs, args) -> str:
    if "business_purpose_raw" in kwargs:
        return kwargs["business_purpose_raw"]
    return args[1] if len(args) > 1 else "Unavailable"
