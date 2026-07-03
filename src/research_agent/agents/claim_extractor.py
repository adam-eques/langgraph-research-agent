from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Claim:
    text: str
    claim_type: str
    confidence: float
    source_offset: int = 0


_CLAIM_PATTERNS = [
    (r"\b(\w[\w\s,]{5,50})\s+(?:is|are|was|were)\s+([\w\s,]{3,50})[.,]", "assertion"),
    (r"\baccording to\s+\w[\w\s]+,?\s+([\w\s,]{10,80})[.,]", "attributed"),
    (r"\bstudies?\s+show\s+(?:that\s+)?([\w\s,]{10,80})[.,]", "evidence"),
    (r"\b(?:in\s+)?(?:20\d\d),?\s+([\w\s,]{10,80})[.,]", "temporal"),
]

_COMPILED = [(re.compile(p, re.I), t) for p, t in _CLAIM_PATTERNS]


def extract_claims(text: str, min_confidence: float = 0.5) -> list[Claim]:
    claims: list[Claim] = []
    for pattern, ctype in _COMPILED:
        for m in pattern.finditer(text):
            claim_text = m.group(0).strip()
            confidence = min(1.0, len(claim_text) / 50)
            if confidence >= min_confidence:
                claims.append(
                    Claim(
                        text=claim_text,
                        claim_type=ctype,
                        confidence=confidence,
                        source_offset=m.start(),
                    )
                )
    return sorted(claims, key=lambda c: c.source_offset)


def filter_claims_by_type(claims: list[Claim], claim_type: str) -> list[Claim]:
    return [c for c in claims if c.claim_type == claim_type]
