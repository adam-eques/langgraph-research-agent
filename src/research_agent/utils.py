from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def hash_query(query: str) -> str:
    """Return a stable SHA-256 hex digest of a query string."""
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()


def truncate(text: str, max_chars: int = 200, suffix: str = "...") -> str:
    """Truncate text to max_chars, appending suffix if truncated."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """Collapse runs of whitespace and strip leading/trailing space."""
    return re.sub(r"\s+", " ", text).strip()


def chunk_list(items: list[Any], size: int) -> list[list[Any]]:
    """Split a list into chunks of at most `size` items."""
    return [items[i : i + size] for i in range(0, len(items), size)]


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator that retries a function on exception with exponential backoff."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise RuntimeError(f"All {max_attempts} attempts failed") from last_exc

        return wrapper  # type: ignore[return-value]

    return decorator


def format_sources(sources: list[str]) -> str:
    """Format a list of source names into a readable citations section."""
    if not sources:
        return ""
    lines = [f"  [{i + 1}] {src}" for i, src in enumerate(sources)]
    return "Sources:\n" + "\n".join(lines)
