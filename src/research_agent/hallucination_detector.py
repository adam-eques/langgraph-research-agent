from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_CONFIDENT_CLAIMS = re.compile(
    r"\b(is|are|was|were|has been|have been|will be|definitely|certainly|always|never)\b",
    re.IGNORECASE,
)
_HEDGE_WORDS = re.compile(
    r"\b(may|might|could|possibly|potentially|seems|appears|suggests|indicates|likely)\b",
    re.IGNORECASE,
)


def detect_overconfident_claims(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    flagged = []
    for s in sentences:
        confident = len(_CONFIDENT_CLAIMS.findall(s))
        hedged = len(_HEDGE_WORDS.findall(s))
        if confident > 2 and hedged == 0 and len(s.split()) > 10:
            flagged.append(s)
    return flagged


def hallucination_risk_score(text: str, supported_facts: list[str]) -> float:
    claims = re.split(r"(?<=[.!?])\s+", text)
    if not claims:
        return 0.0
    unsupported = 0
    for claim in claims:
        cl = claim.lower()
        if not any(fact.lower()[:40] in cl for fact in supported_facts):
            unsupported += 1
    return round(unsupported / max(len(claims), 1), 3)
