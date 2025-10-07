from __future__ import annotations

from typing import Any


def filter_by_min_length(docs: list[dict], min_chars: int = 100) -> list[dict]:
    return [d for d in docs if len(d.get("content", "")) >= min_chars]


def filter_by_source_domain(docs: list[dict], blocked_domains: set[str]) -> list[dict]:
    filtered = []
    for d in docs:
        source = d.get("source", "")
        domain = source.split("/")[2] if source.startswith("http") else source
        if not any(bd in domain for bd in blocked_domains):
            filtered.append(d)
    return filtered


def filter_by_score(docs: list[dict], min_score: float = 0.0) -> list[dict]:
    return [d for d in docs if d.get("score", 0.0) >= min_score]


def filter_by_metadata_key(docs: list[dict], key: str, value: Any) -> list[dict]:
    return [d for d in docs if d.get("metadata", {}).get(key) == value]


def apply_filters(
    docs: list[dict],
    min_length: int = 50,
    min_score: float = 0.0,
    blocked_domains: set[str] | None = None,
) -> list[dict]:
    result = filter_by_min_length(docs, min_length)
    result = filter_by_score(result, min_score)
    if blocked_domains:
        result = filter_by_source_domain(result, blocked_domains)
    return result
