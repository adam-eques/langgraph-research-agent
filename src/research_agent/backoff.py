from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

_MAX_RETRY_DELAY = 32.0  # seconds


async def call_with_backoff(
    fn,
    *args,
    max_attempts: int = 4,
    base_delay: float = 1.0,
    **kwargs,
) -> Any:
    """Call async fn with exponential backoff on failure."""
    delay = base_delay
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt == max_attempts:
                break
            logger.warning(
                "Attempt %d/%d failed: %s — retrying in %.1fs",
                attempt,
                max_attempts,
                exc,
                delay,
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, _MAX_RETRY_DELAY)
    raise RuntimeError(f"All {max_attempts} attempts failed") from last_exc
