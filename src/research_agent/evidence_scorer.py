from __future__ import annotations

import re

_STRONG_SIGNALS = [
    r"\bstud(y|ies)\b",
    r"\bresearch\b",
    r"\bpaper\b",
    r"\bjournal\b",
    r"\bpeer.reviewed\b",
    r"\bpublished\b",
    r"\bdata shows?\b",
]

_WEAK_SIGNALS = [
    r"\bsome say\b",
    r"\bit is believed\b",
    r"\bpossibly\b",
    r"\bmight\b",
    r"\bmaybe\b",
    r"\bunclear\b",
]


def score_evidence_strength(text: str) -> float:
    t = text.lower()
    strong = sum(1 for p in _STRONG_SIGNALS if re.search(p, t))
    weak = sum(1 for p in _WEAK_SIGNALS if re.search(p, t))
    score = min(1.0, max(0.0, 0.5 + (strong * 0.1) - (weak * 0.1)))
    return round(score, 3)


def classify_evidence(score: float) -> str:
    if score >= 0.75:
        return "strong"
    if score >= 0.5:
        return "moderate"
    return "weak"
