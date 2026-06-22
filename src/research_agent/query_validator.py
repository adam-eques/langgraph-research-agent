from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    code: str
    message: str


@dataclass
class QueryValidationResult:
    query: str
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    normalized: str = ""

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "is_valid": self.is_valid,
            "errors": [{"code": e.code, "message": e.message} for e in self.errors],
            "normalized": self.normalized,
        }


_INJECTION_RE = re.compile(
    r"(ignore previous|disregard all|forget instructions|you are now|act as if)", re.I
)


def validate_query(
    query: str,
    min_length: int = 3,
    max_length: int = 1000,
    allow_empty: bool = False,
) -> QueryValidationResult:
    errors: list[ValidationError] = []
    normalized = query.strip()

    if not normalized and not allow_empty:
        errors.append(ValidationError("EMPTY", "Query must not be empty."))
    elif len(normalized) < min_length:
        errors.append(ValidationError("TOO_SHORT", f"Query must be at least {min_length} characters."))

    if len(normalized) > max_length:
        errors.append(ValidationError("TOO_LONG", f"Query exceeds {max_length} character limit."))

    if _INJECTION_RE.search(normalized):
        errors.append(ValidationError("INJECTION", "Query contains disallowed instruction patterns."))

    return QueryValidationResult(
        query=query,
        is_valid=len(errors) == 0,
        errors=errors,
        normalized=normalized,
    )


def batch_validate(queries: list[str], **kwargs) -> list[QueryValidationResult]:
    return [validate_query(q, **kwargs) for q in queries]


def filter_valid(queries: list[str], **kwargs) -> list[str]:
    return [q for q in queries if validate_query(q, **kwargs).is_valid]
