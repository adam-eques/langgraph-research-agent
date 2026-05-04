from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    issues: list[str]
    score: float

    @property
    def passed(self) -> bool:
        return self.valid and self.score >= 0.6


def check_min_length(text: str, min_chars: int = 50) -> str | None:
    if len(text.strip()) < min_chars:
        return f"Response too short: {len(text)} chars (min {min_chars})"
    return None


def check_not_empty(text: str) -> str | None:
    if not text.strip():
        return "Response is empty"
    return None


def check_no_refusal_pattern(text: str) -> str | None:
    refusal_patterns = [
        r"\bi (cannot|can't|won't|refuse to)\b",
        r"\bas an ai\b",
        r"\bi'm not able to\b",
    ]
    for pat in refusal_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return f"Possible refusal detected: matched '{pat}'"
    return None


def check_factual_markers(text: str) -> str | None:
    vague_patterns = [r"\bmaybe\b", r"\bi think\b", r"\bprobably\b", r"\bnot sure\b"]
    count = sum(1 for p in vague_patterns if re.search(p, text, re.I))
    if count >= 3:
        return f"Response contains {count} hedge phrases suggesting low confidence"
    return None


def validate_response(text: str, min_chars: int = 50) -> ValidationResult:
    checks = [
        check_not_empty(text),
        check_min_length(text, min_chars),
        check_no_refusal_pattern(text),
        check_factual_markers(text),
    ]
    issues = [c for c in checks if c is not None]
    score = 1.0 - (len(issues) * 0.25)
    return ValidationResult(valid=len(issues) == 0, issues=issues, score=max(0.0, score))
