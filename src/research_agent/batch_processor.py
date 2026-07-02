from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    total: int
    succeeded: int
    failed: int
    results: list[Any]
    errors: list[str]

    @property
    def success_rate(self) -> float:
        return self.succeeded / self.total if self.total > 0 else 0.0


async def process_batch(
    items: list[Any],
    processor: Callable[[Any], Awaitable[Any]],
    batch_size: int = 10,
    concurrency: int = 5,
    on_error: str = "continue",
) -> BatchResult:
    results = []
    errors = []
    sem = asyncio.Semaphore(concurrency)

    async def process_one(item: Any) -> Any:
        async with sem:
            return await processor(item)

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_results = await asyncio.gather(
            *[process_one(item) for item in batch],
            return_exceptions=True,
        )
        for r in batch_results:
            if isinstance(r, Exception):
                errors.append(str(r))
                results.append(None)
                if on_error == "raise":
                    raise r
            else:
                results.append(r)

    succeeded = sum(1 for r in results if r is not None)
    return BatchResult(
        total=len(items),
        succeeded=succeeded,
        failed=len(errors),
        results=results,
        errors=errors,
    )
