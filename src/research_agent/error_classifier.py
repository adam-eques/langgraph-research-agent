from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ErrorCategory(str, Enum):
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTH = "auth"
    PARSING = "parsing"
    VALIDATION = "validation"
    LLM = "llm"
    RETRIEVAL = "retrieval"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedError:
    category: ErrorCategory
    retryable: bool
    message: str
    original: Exception | None = None


_ERROR_SIGNATURES: list[tuple[list[str], ErrorCategory, bool]] = [
    (["connection", "network", "dns", "resolve"], ErrorCategory.NETWORK, True),
    (["timeout", "timed out", "deadline"], ErrorCategory.TIMEOUT, True),
    (["rate limit", "429", "quota", "too many requests"], ErrorCategory.RATE_LIMIT, True),
    (["401", "403", "unauthorized", "forbidden", "api key"], ErrorCategory.AUTH, False),
    (["json", "parse", "decode", "unexpected token"], ErrorCategory.PARSING, False),
    (["validation", "invalid input", "schema"], ErrorCategory.VALIDATION, False),
    (["anthropic", "openai", "claude", "gpt", "completion"], ErrorCategory.LLM, True),
    (["retrieval", "chroma", "vector", "embedding"], ErrorCategory.RETRIEVAL, True),
]


def classify_error(exc: Exception) -> ClassifiedError:
    msg = str(exc).lower()
    for keywords, category, retryable in _ERROR_SIGNATURES:
        if any(kw in msg for kw in keywords):
            return ClassifiedError(
                category=category,
                retryable=retryable,
                message=str(exc),
                original=exc,
            )
    return ClassifiedError(
        category=ErrorCategory.UNKNOWN,
        retryable=False,
        message=str(exc),
        original=exc,
    )


def is_retryable(exc: Exception) -> bool:
    return classify_error(exc).retryable
