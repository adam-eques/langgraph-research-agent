from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_SENSITIVE_KEYS = {"api_key", "token", "secret", "password", "authorization"}


def redact(data: Any, depth: int = 0) -> Any:
    """Recursively redact sensitive keys from dicts for safe logging."""
    if depth > 6:
        return data
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k.lower() in _SENSITIVE_KEYS else redact(v, depth + 1)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [redact(item, depth + 1) for item in data]
    return data


def safe_log_request(data: dict, label: str = "request") -> None:
    logger.debug("%s: %s", label, redact(data))
