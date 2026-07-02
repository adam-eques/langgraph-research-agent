from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass
class DeduplicationResult:
    original_count: int
    deduplicated_count: int
    removed_indices: list[int]
    unique_queries: list[str]

    def reduction_pct(self) -> float:
        if self.original_count == 0:
            return 0.0
        return (self.original_count - self.deduplicated_count) / self.original_count * 100


def _normalize(query: str) -> str:
    q = query.lower().strip()
    q = re.sub(r"\s+", " ", q)
    q = re.sub(r"[?.!,]+$", "", q)
    return q


def _query_hash(query: str) -> str:
    return hashlib.md5(_normalize(query).encode()).hexdigest()


def _jaccard_similarity(a: str, b: str) -> float:
    set_a = set(_normalize(a).split())
    set_b = set(_normalize(b).split())
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def deduplicate_exact(queries: list[str]) -> DeduplicationResult:
    seen: dict[str, int] = {}
    removed: list[int] = []
    unique: list[str] = []
    for i, q in enumerate(queries):
        h = _query_hash(q)
        if h in seen:
            removed.append(i)
        else:
            seen[h] = i
            unique.append(q)
    return DeduplicationResult(
        original_count=len(queries),
        deduplicated_count=len(unique),
        removed_indices=removed,
        unique_queries=unique,
    )


def deduplicate_fuzzy(
    queries: list[str],
    similarity_threshold: float = 0.8,
) -> DeduplicationResult:
    removed: list[int] = []
    unique: list[str] = []
    for i, q in enumerate(queries):
        is_dup = any(_jaccard_similarity(q, prev) >= similarity_threshold for prev in unique)
        if is_dup:
            removed.append(i)
        else:
            unique.append(q)
    return DeduplicationResult(
        original_count=len(queries),
        deduplicated_count=len(unique),
        removed_indices=removed,
        unique_queries=unique,
    )


def deduplicate(
    queries: list[str],
    fuzzy: bool = False,
    threshold: float = 0.8,
) -> list[str]:
    if fuzzy:
        return deduplicate_fuzzy(queries, threshold).unique_queries
    return deduplicate_exact(queries).unique_queries
