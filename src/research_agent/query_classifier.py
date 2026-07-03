from __future__ import annotations

import re
from enum import StrEnum


class QueryType(StrEnum):
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    OPINION = "opinion"


_PATTERNS: dict[QueryType, list[str]] = {
    QueryType.FACTUAL: [r"what is", r"who is", r"when did", r"where is", r"define"],
    QueryType.ANALYTICAL: [r"why", r"explain", r"how does", r"what causes"],
    QueryType.COMPARATIVE: [r"compare", r"vs\.?", r"difference between", r"better than"],
    QueryType.PROCEDURAL: [r"how to", r"steps to", r"how do i", r"guide to"],
    QueryType.OPINION: [r"should i", r"is it good", r"best way", r"recommend"],
}


def classify_query(query: str) -> QueryType:
    q = query.lower()
    for qtype, patterns in _PATTERNS.items():
        if any(re.search(p, q) for p in patterns):
            return qtype
    return QueryType.FACTUAL
