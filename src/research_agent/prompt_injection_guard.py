from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions|prompts?|context)",
    r"forget\s+(everything|what|all\s+previous)",
    r"you\s+are\s+now\s+(a\s+)?(?:an?\s+)?\w+",
    r"act\s+as\s+(?:if\s+)?(?:a\s+)?(?:an?\s+)?\w+\s+with\s+no\s+restrictions",
    r"pretend\s+(?:you\s+are|to\s+be)\s+(?:a\s+)?",
    r"jailbreak",
    r"DAN\s*mode",
    r"system\s*prompt\s*:",
    r"\[INST\]",
    r"<\|system\|>",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def is_injection_attempt(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


def sanitize_query(text: str, replacement: str = "[FILTERED]") -> str:
    for pattern in _COMPILED:
        if pattern.search(text):
            logger.warning("Potential prompt injection detected; sanitizing")
            return replacement
    return text


def score_injection_risk(text: str) -> float:
    matches = sum(1 for p in _COMPILED if p.search(text))
    return min(1.0, matches / len(_COMPILED) * 3)
