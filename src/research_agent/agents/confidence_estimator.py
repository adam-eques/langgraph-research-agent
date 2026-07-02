from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_HIGH_CONFIDENCE_WORDS = ["confirmed", "proven", "established", "demonstrated", "according to"]
_LOW_CONFIDENCE_WORDS = ["possibly", "might", "unclear", "uncertain", "debated", "some argue"]


def estimate_confidence(answer: str, citations: list[dict]) -> float:
    a = answer.lower()
    high = sum(1 for w in _HIGH_CONFIDENCE_WORDS if w in a)
    low = sum(1 for w in _LOW_CONFIDENCE_WORDS if w in a)
    citation_bonus = min(0.3, len(citations) * 0.05)
    base = 0.5 + (high - low) * 0.05 + citation_bonus
    return round(min(1.0, max(0.0, base)), 3)


def confidence_label(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"
