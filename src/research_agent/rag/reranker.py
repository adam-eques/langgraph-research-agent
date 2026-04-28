from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class RankedDoc:
    content: str
    original_score: float
    rerank_score: float
    source: str = ""

    @property
    def final_score(self) -> float:
        return 0.4 * self.original_score + 0.6 * self.rerank_score


def cross_encoder_score(query: str, doc: str) -> float:
    query_terms = set(query.lower().split())
    doc_terms = doc.lower().split()
    if not doc_terms:
        return 0.0
    overlap = sum(1 for t in doc_terms if t in query_terms)
    idf_boost = math.log(1 + len(doc_terms))
    return min(1.0, overlap / max(len(query_terms), 1) * (1.0 + 0.1 * idf_boost))


def rerank(
    query: str,
    documents: list[dict],
    top_k: int = 5,
    content_key: str = "content",
    score_key: str = "score",
) -> list[RankedDoc]:
    ranked = []
    for doc in documents:
        content = doc.get(content_key, "")
        original_score = doc.get(score_key, 0.5)
        rerank_score = cross_encoder_score(query, content)
        ranked.append(RankedDoc(
            content=content,
            original_score=original_score,
            rerank_score=rerank_score,
            source=doc.get("source", ""),
        ))
    ranked.sort(key=lambda d: d.final_score, reverse=True)
    return ranked[:top_k]
