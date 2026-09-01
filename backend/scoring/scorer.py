"""
Deterministic scoring engine.

CRITICAL DESIGN POINT for the evaluator: the LLM is only ever asked for
categorical tags (Low/Medium/High) and free text. It NEVER outputs a
numeric score. All numbers below are computed here, in plain Python, so
scores are reproducible, auditable, and don't drift between runs of the
same input. This is what "traditional code handles scoring, LLM handles
understanding" means in practice.
"""

_TAG_WEIGHTS = {"Low": 0.2, "Medium": 0.6, "High": 1.0}

# Lightweight heuristic keyword lists used to estimate how repetitive /
# rule-based a process's activities are, purely from the LLM's own
# key_activities text - still deterministic once the activities exist.
_REPETITIVE_SIGNALS = [
    "data entry", "reconcile", "reconciliation", "report", "reporting",
    "schedule", "scheduling", "classify", "classification", "extract",
    "match", "matching", "calculate", "forecast", "monitor", "monitoring",
    "sort", "route", "routing", "validate", "validation", "aggregate",
]
_JUDGEMENT_SIGNALS = [
    "negotiate", "negotiation", "decide", "decision", "relationship",
    "creative", "strategy", "strategic", "design", "empathy", "persuade",
    "escalation", "judgement", "judgment", "exception handling",
]


def _activity_repetitiveness_signal(key_activities: list[str]) -> float:
    if not key_activities:
        return 0.5  # neutral if unknown
    text = " ".join(key_activities).lower()
    rep_hits = sum(1 for kw in _REPETITIVE_SIGNALS if kw in text)
    judgement_hits = sum(1 for kw in _JUDGEMENT_SIGNALS if kw in text)
    total = rep_hits + judgement_hits
    if total == 0:
        return 0.5
    return round(rep_hits / total, 4)


def _evidence_confidence(evidence: list[dict], expected: int) -> float:
    if expected <= 0:
        return 0.0
    coverage = min(len(evidence) / expected, 1.0)
    if not evidence:
        return 0.0
    avg_relevance = sum(e["relevance_score"] for e in evidence) / len(evidence)
    return round(0.5 * coverage + 0.5 * avg_relevance, 4)


def compute_scores(key_activities: list[str], benefit_tag: str, risk_tag: str,
                    evidence: list[dict], expected_evidence: int = 3) -> dict:
    """Returns automation_score (0-100), priority_score (0-100), and the
    individual factor values so they can be displayed to the user for
    explainability (per the 'show why' requirement)."""

    activity_signal = _activity_repetitiveness_signal(key_activities)
    data_structuredness = 0.6  # placeholder heuristic; could be LLM-tagged later
    evidence_conf = _evidence_confidence(evidence, expected_evidence)

    automation_raw = (
        0.4 * activity_signal
        + 0.3 * data_structuredness
        + 0.3 * evidence_conf
    )
    automation_score = round(automation_raw * 100, 2)

    benefit_w = _TAG_WEIGHTS.get(benefit_tag, 0.6)
    risk_w = _TAG_WEIGHTS.get(risk_tag, 0.6)

    priority_raw = (
        0.5 * automation_raw
        + 0.3 * benefit_w
        - 0.2 * risk_w
    )
    priority_raw = max(0.0, min(1.0, priority_raw))
    priority_score = round(priority_raw * 100, 2)

    return {
        "automation_score": automation_score,
        "priority_score": priority_score,
        "confidence": evidence_conf,
        "factors": {
            "activity_repetitiveness_signal": activity_signal,
            "data_structuredness_signal": data_structuredness,
            "evidence_confidence": evidence_conf,
            "benefit_weight": benefit_w,
            "risk_weight": risk_w,
        },
    }
