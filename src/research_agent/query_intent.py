from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class IntentType(StrEnum):
    RESEARCH = "research"
    SUMMARIZE = "summarize"
    COMPARE = "compare"
    EXPLAIN = "explain"
    FIND = "find"
    UNKNOWN = "unknown"


@dataclass
class QueryIntent:
    intent: IntentType
    confidence: float
    entities: list[str]
    keywords: list[str]


_INTENT_PATTERNS = {
    IntentType.SUMMARIZE: [r"\bsummariz\w+\b", r"\boverall\b", r"\bbriefly\b", r"\btldr\b"],
    IntentType.COMPARE: [
        r"\bcompare\b",
        r"\bvs\b",
        r"\bversus\b",
        r"\bdifference\b",
        r"\bbetter\b",
    ],
    IntentType.EXPLAIN: [r"\bexplain\b", r"\bhow does\b", r"\bwhy does\b", r"\bwhat is\b"],
    IntentType.FIND: [r"\bfind\b", r"\blocate\b", r"\bwhere is\b", r"\blist\b"],
    IntentType.RESEARCH: [r"\bresearch\b", r"\banalyz\w+\b", r"\binvestigat\w+\b", r"\bstudy\b"],
}


def detect_intent(query: str) -> QueryIntent:
    q = query.lower()
    best = IntentType.UNKNOWN
    best_count = 0
    for intent, patterns in _INTENT_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, q))
        if count > best_count:
            best_count = count
            best = intent
    confidence = min(1.0, best_count * 0.4) if best_count else 0.0
    words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", query)
    entities = list(dict.fromkeys(words))[:5]
    keywords = [
        w for w in re.findall(r"\b\w{4,}\b", q) if w not in {"what", "that", "this", "with", "from"}
    ][:8]
    return QueryIntent(intent=best, confidence=confidence, entities=entities, keywords=keywords)
