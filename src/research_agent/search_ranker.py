from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    doc_id: str
    content: str
    base_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedSearchResult:
    doc_id: str
    content: str
    final_score: float
    rank: int
    signals: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "rank": self.rank,
            "final_score": round(self.final_score, 4),
            "signals": {k: round(v, 4) for k, v in self.signals.items()},
        }


def _query_coverage(content: str, query_terms: list[str]) -> float:
    if not query_terms:
        return 0.0
    text = content.lower()
    matched = sum(1 for t in query_terms if t.lower() in text)
    return matched / len(query_terms)


def _freshness_score(metadata: dict) -> float:
    year = metadata.get("year")
    if year is None:
        return 0.5
    current_year = 2026
    age = max(0, current_year - int(year))
    return max(0.0, 1.0 - age * 0.05)


def _length_score(content: str, ideal: int = 500) -> float:
    length = len(content)
    if length == 0:
        return 0.0
    return 1.0 - abs(length - ideal) / max(ideal, length)


def rank_search_results(
    results: list[SearchResult],
    query: str,
    weights: dict[str, float] | None = None,
) -> list[RankedSearchResult]:
    default_weights = {"base": 0.5, "coverage": 0.3, "freshness": 0.1, "length": 0.1}
    w = {**default_weights, **(weights or {})}
    query_terms = re.findall(r"\b\w{3,}\b", query.lower())

    ranked: list[RankedSearchResult] = []
    for r in results:
        signals = {
            "base": r.base_score,
            "coverage": _query_coverage(r.content, query_terms),
            "freshness": _freshness_score(r.metadata),
            "length": _length_score(r.content),
        }
        final = sum(w.get(k, 0.0) * v for k, v in signals.items())
        ranked.append(RankedSearchResult(
            doc_id=r.doc_id,
            content=r.content,
            final_score=final,
            rank=0,
            signals=signals,
        ))

    ranked.sort(key=lambda r: -r.final_score)
    for i, r in enumerate(ranked):
        r.rank = i + 1
    return ranked
