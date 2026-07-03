from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

logger = logging.getLogger(__name__)


async def run_multi_query(
    queries: list[str],
    search_fn,
    concurrency: int = 3,
) -> list[dict[str, Any]]:
    """Run multiple queries concurrently and collect results."""
    semaphore = asyncio.Semaphore(concurrency)

    async def _run(q: str) -> dict:
        async with semaphore:
            try:
                result = await search_fn(q)
                return {"query": q, "result": result, "error": None}
            except Exception as exc:
                logger.warning("Query failed: %s — %s", q[:60], exc)
                return {"query": q, "result": None, "error": str(exc)}

    tasks = [_run(q) for q in queries]
    return cast(list[dict[str, Any]], await asyncio.gather(*tasks))


def deduplicate_results(results: list[dict]) -> list[dict]:
    """Remove duplicate results by query text."""
    seen, unique = set(), []
    for r in results:
        key = r.get("query", "").lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique
