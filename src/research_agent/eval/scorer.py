from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def score_answer_length(answer: str, min_words: int = 50, max_words: int = 800) -> float:
    count = len(answer.split())
    if count < min_words:
        return count / min_words
    if count > max_words:
        return max_words / count
    return 1.0


def score_citation_coverage(answer: str, citations: list[dict]) -> float:
    if not citations:
        return 1.0
    referenced = sum(
        1 for c in citations
        if c.get("source", "").split("/")[-1][:12] in answer
    )
    return referenced / len(citations)


def composite_score(
    answer: str,
    citations: list[dict],
    faithfulness: float,
    relevance: float,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or {"faithfulness": 0.4, "relevance": 0.3, "length": 0.2, "citation": 0.1}
    length = score_answer_length(answer)
    citation = score_citation_coverage(answer, citations)
    return (
        w.get("faithfulness", 0.4) * faithfulness
        + w.get("relevance", 0.3) * relevance
        + w.get("length", 0.2) * length
        + w.get("citation", 0.1) * citation
    )
