from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class QueryCacheWarmer:
    """Pre-populate a cache with results for frequently asked queries."""

    def __init__(
        self,
        search_fn: Callable,
        cache,
        concurrency: int = 3,
    ) -> None:
        self._search = search_fn
        self._cache = cache
        self._concurrency = concurrency

    async def warm(self, queries: list[str]) -> dict[str, bool]:
        sem = asyncio.Semaphore(self._concurrency)
        results: dict[str, bool] = {}

        async def _warm_one(q: str) -> None:
            async with sem:
                if self._cache.get(q) is not None:
                    results[q] = False
                    logger.debug("Cache already warm for query: %s", q[:60])
                    return
                try:
                    result = await self._search(q)
                    self._cache.set(q, result)
                    results[q] = True
                    logger.debug("Warmed cache for: %s", q[:60])
                except Exception as exc:
                    results[q] = False
                    logger.warning("Cache warm failed for %s: %s", q[:60], exc)

        await asyncio.gather(*[_warm_one(q) for q in queries])
        return results
