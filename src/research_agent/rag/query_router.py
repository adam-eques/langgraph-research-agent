from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class RetrievalStrategy(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    MULTI_HOP = "multi_hop"
    DIRECT = "direct"


@dataclass
class RoutingDecision:
    strategy: RetrievalStrategy
    confidence: float
    reason: str
    suggested_top_k: int = 5

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy.value,
            "confidence": round(self.confidence, 4),
            "reason": self.reason,
            "suggested_top_k": self.suggested_top_k,
        }


_KEYWORD_SIGNALS = [
    re.compile(r"\b(find|search for|look up|list all|show me)\b", re.I),
    re.compile(r'"[^"]{3,}"'),
]

_MULTI_HOP_SIGNALS = [
    re.compile(r"\b(because|therefore|as a result of|which led to|due to)\b", re.I),
    re.compile(r"\b(and then|followed by|subsequently|after that)\b", re.I),
]

_DIRECT_SIGNALS = [
    re.compile(r"\bwhat is (the )?definition of\b", re.I),
    re.compile(r"\bwho is\b", re.I),
    re.compile(r"\bwhen (was|did|is)\b", re.I),
]


def route_query(query: str, default_top_k: int = 5) -> RoutingDecision:
    for pat in _DIRECT_SIGNALS:
        if pat.search(query):
            return RoutingDecision(
                strategy=RetrievalStrategy.DIRECT,
                confidence=0.85,
                reason="Factual lookup query detected.",
                suggested_top_k=3,
            )

    for pat in _MULTI_HOP_SIGNALS:
        if pat.search(query):
            return RoutingDecision(
                strategy=RetrievalStrategy.MULTI_HOP,
                confidence=0.75,
                reason="Multi-hop reasoning signals detected.",
                suggested_top_k=default_top_k + 3,
            )

    kw_hits = sum(1 for pat in _KEYWORD_SIGNALS if pat.search(query))
    if kw_hits >= 1:
        return RoutingDecision(
            strategy=RetrievalStrategy.KEYWORD,
            confidence=0.7,
            reason="Explicit keyword or list request detected.",
            suggested_top_k=default_top_k,
        )

    return RoutingDecision(
        strategy=RetrievalStrategy.HYBRID,
        confidence=0.6,
        reason="No strong signal; defaulting to hybrid retrieval.",
        suggested_top_k=default_top_k,
    )
