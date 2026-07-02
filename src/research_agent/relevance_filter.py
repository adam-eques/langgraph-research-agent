from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def compute_keyword_overlap(query: str, text: str) -> float:
    q_words = set(re.findall(r"\b\w{3,}\b", query.lower()))
    t_words = set(re.findall(r"\b\w{3,}\b", text.lower()))
    if not q_words:
        return 0.0
    return len(q_words & t_words) / len(q_words)


def filter_relevant(
    query: str,
    documents: list[str],
    threshold: float = 0.2,
) -> list[str]:
    results = []
    for doc in documents:
        score = compute_keyword_overlap(query, doc)
        if score >= threshold:
            results.append(doc)
        else:
            logger.debug(
                "Filtered out document with overlap=%.2f (threshold=%.2f)", score, threshold
            )
    return results


def rank_by_relevance(query: str, documents: list[str]) -> list[tuple[float, str]]:
    scored = [(compute_keyword_overlap(query, d), d) for d in documents]
    return sorted(scored, key=lambda x: x[0], reverse=True)
