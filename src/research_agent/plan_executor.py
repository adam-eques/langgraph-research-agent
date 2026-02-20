from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class PlanExecutor:
    """Execute a planner-generated list of sub-queries in sequence or parallel."""

    def __init__(self, search_fn: Callable, concurrency: int = 3) -> None:
        self._search = search_fn
        self._concurrency = concurrency

    async def execute_sequential(self, queries: list[str]) -> list[dict]:
        results = []
        for q in queries:
            try:
                result = await self._search(q)
                results.append({"query": q, "result": result, "ok": True})
            except Exception as exc:
                logger.warning("Sub-query failed: %s", exc)
                results.append({"query": q, "result": None, "ok": False, "error": str(exc)})
        return results

    async def execute_parallel(self, queries: list[str]) -> list[dict]:
        sem = asyncio.Semaphore(self._concurrency)

        async def _run(q: str) -> dict:
            async with sem:
                try:
                    result = await self._search(q)
                    return {"query": q, "result": result, "ok": True}
                except Exception as exc:
                    return {"query": q, "result": None, "ok": False, "error": str(exc)}

        return list(await asyncio.gather(*[_run(q) for q in queries]))
