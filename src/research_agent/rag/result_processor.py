from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def merge_retrieval_results(
    results_a: list[dict],
    results_b: list[dict],
    key: str = "page_content",
) -> list[dict]:
    seen, merged = set(), []
    for doc in results_a + results_b:
        content = doc.get(key, "")[:80]
        if content not in seen:
            seen.add(content)
            merged.append(doc)
    return merged


def normalize_scores(docs: list[dict], score_key: str = "score") -> list[dict]:
    scores = [d.get(score_key, 0.0) for d in docs]
    max_s = max(scores) if scores else 1.0
    min_s = min(scores) if scores else 0.0
    rng = max_s - min_s or 1.0
    return [{**d, score_key: round((d.get(score_key, 0.0) - min_s) / rng, 4)} for d in docs]


def top_k_by_score(docs: list[dict], k: int, score_key: str = "score") -> list[dict]:
    return sorted(docs, key=lambda d: d.get(score_key, 0.0), reverse=True)[:k]
