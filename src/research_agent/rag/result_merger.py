from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MergedResult:
    doc_id: str
    content: str
    score: float
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "content": self.content[:300],
            "score": round(self.score, 4),
            "sources": self.sources,
        }


def _normalize_scores(results: list[dict]) -> list[dict]:
    if not results:
        return results
    max_score = max(r.get("score", 0.0) for r in results)
    if max_score == 0:
        return results
    return [{**r, "score": r.get("score", 0.0) / max_score} for r in results]


def merge_results(
    result_sets: list[list[dict]],
    dedup_field: str = "doc_id",
    score_agg: str = "max",
    top_k: int = 10,
) -> list[MergedResult]:
    doc_map: dict[str, list[dict]] = {}

    for source_idx, result_set in enumerate(result_sets):
        normalized = _normalize_scores(result_set)
        for item in normalized:
            key = str(item.get(dedup_field, ""))
            if key not in doc_map:
                doc_map[key] = []
            doc_map[key].append({**item, "_source_idx": source_idx})

    merged: list[MergedResult] = []
    for doc_id, items in doc_map.items():
        scores = [i.get("score", 0.0) for i in items]
        if score_agg == "max":
            final_score = max(scores)
        elif score_agg == "mean":
            final_score = sum(scores) / len(scores)
        elif score_agg == "sum":
            final_score = sum(scores)
        else:
            final_score = max(scores)

        content = items[0].get("content", "")
        sources = list({str(i.get("_source_idx", "")) for i in items})
        metadata = {k: v for k, v in items[0].items() if not k.startswith("_") and k != "score"}

        merged.append(
            MergedResult(
                doc_id=doc_id,
                content=content,
                score=final_score,
                sources=sources,
                metadata=metadata,
            )
        )

    return sorted(merged, key=lambda r: -r.score)[:top_k]


def deduplicate_results(
    results: list[dict], field: str = "content", threshold: float = 0.9
) -> list[dict]:
    seen: list[str] = []
    unique: list[dict] = []
    for r in results:
        text = r.get(field, "")
        words = set(text.lower().split())
        is_dup = False
        for prev in seen:
            prev_words = set(prev.lower().split())
            if words and prev_words:
                overlap = len(words & prev_words) / max(len(words), len(prev_words))
                if overlap >= threshold:
                    is_dup = True
                    break
        if not is_dup:
            seen.append(text)
            unique.append(r)
    return unique
