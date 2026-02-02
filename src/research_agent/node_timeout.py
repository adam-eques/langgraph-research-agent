from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def with_timeout(seconds: float, node_name: str | None = None):
    """Async decorator that raises asyncio.TimeoutError if function exceeds deadline."""
    def decorator(fn: Callable) -> Callable:
        name = node_name or fn.__name__
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(fn(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error("Node %r timed out after %.1fs", name, seconds)
                raise
        return wrapper
    return decorator
