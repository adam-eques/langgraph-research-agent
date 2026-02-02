from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Contradiction:
    claim_a: str
    claim_b: str
    reason: str
    confidence: float = 0.7


_NEGATION_PATTERNS = [
    (r"\b(is|are|was|were)\b", r"\b(is not|are not|was not|were not|isn't|aren't|wasn't|weren't)\b"),
    (r"\bcan\b", r"\bcannot\b|\bcan't\b"),
    (r"\bwill\b", r"\bwill not\b|\bwon't\b"),
    (r"\bhas\b", r"\bhas not\b|\bhasn't\b"),
]


def _extract_subject_predicate(sentence: str) -> tuple[str, str]:
    words = sentence.lower().split()
    return " ".join(words[:2]) if len(words) >= 2 else ("", "")


def detect_contradictions(claims: list[str]) -> list[Contradiction]:
    contradictions = []
    for i, c_a in enumerate(claims):
        for j, c_b in enumerate(claims):
            if i >= j:
                continue
            subj_a, pred_a = _extract_subject_predicate(c_a)
            subj_b, pred_b = _extract_subject_predicate(c_b)
            if subj_a and subj_a == subj_b:
                for pos_pat, neg_pat in _NEGATION_PATTERNS:
                    if (re.search(pos_pat, c_a, re.I) and re.search(neg_pat, c_b, re.I)):
                        contradictions.append(Contradiction(
                            claim_a=c_a, claim_b=c_b,
                            reason="subject-predicate negation", confidence=0.75,
                        ))
                    elif (re.search(neg_pat, c_a, re.I) and re.search(pos_pat, c_b, re.I)):
                        contradictions.append(Contradiction(
                            claim_a=c_a, claim_b=c_b,
                            reason="subject-predicate negation (reversed)", confidence=0.75,
                        ))
    return contradictions


def has_contradictions(claims: list[str]) -> bool:
    return len(detect_contradictions(claims)) > 0
