from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


async def with_fallback(
    primary: Callable,
    fallback: Callable,
    *args,
    **kwargs,
) -> Any:
    """Try primary function; on failure log and run fallback."""
    try:
        return await primary(*args, **kwargs)
    except Exception as exc:
        logger.warning("Primary function failed: %s — falling back", exc)
        return await fallback(*args, **kwargs)


async def with_default_on_error(
    fn: Callable,
    default: Any,
    *args,
    **kwargs,
) -> Any:
    """Return default value if fn raises any exception."""
    try:
        return await fn(*args, **kwargs)
    except Exception as exc:
        logger.debug("Function failed, using default: %s", exc)
        return default


def safe_dict_get(data: dict, *keys: str, default: Any = None) -> Any:
    val = data
    for k in keys:
        if not isinstance(val, dict):
            return default
        val = val.get(k, default)
    return val
