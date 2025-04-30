from __future__ import annotations

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def timed(label: str | None = None):
    """Decorator that logs wall-clock time of a function call."""
    def decorator(fn: Callable) -> Callable:
        name = label or fn.__name__
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            t0 = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            logger.debug("%s completed in %.1fms", name, elapsed)
            return result
        return wrapper
    return decorator


def async_timed(label: str | None = None):
    """Async version of timed decorator."""
    def decorator(fn: Callable) -> Callable:
        name = label or fn.__name__
        @wraps(fn)
        async def wrapper(*args, **kwargs) -> Any:
            t0 = time.perf_counter()
            result = await fn(*args, **kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            logger.debug("%s completed in %.1fms", name, elapsed)
            return result
        return wrapper
    return decorator
