from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def check_answer_completeness(query: str, answer: str) -> dict[str, Any]:
    q_words = set(re.findall(r"\b\w{4,}\b", query.lower()))
    a_words = set(re.findall(r"\b\w{4,}\b", answer.lower()))
    coverage = len(q_words & a_words) / max(len(q_words), 1)
    word_count = len(answer.split())
    checks = {
        "word_count": word_count,
        "query_coverage": round(coverage, 3),
        "has_sentences": bool(re.search(r"[.!?]", answer)),
        "not_empty": bool(answer.strip()),
        "not_too_short": word_count >= 20,
    }
    checks["passed"] = all(v is True or (isinstance(v, (int, float)) and v > 0)
                           for v in checks.values())
    return checks


def is_answer_acceptable(query: str, answer: str, min_coverage: float = 0.2) -> bool:
    result = check_answer_completeness(query, answer)
    return result.get("not_empty", False) and result.get("query_coverage", 0) >= min_coverage
