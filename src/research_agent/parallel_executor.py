from __future__ import annotations

import asyncio
from typing import Any, Callable, Awaitable


async def run_parallel(
    tasks: list[tuple[str, Callable[..., Awaitable[Any]], tuple, dict]],
    concurrency: int = 5,
    timeout: float | None = None,
) -> dict[str, Any]:
    sem = asyncio.Semaphore(concurrency)
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}

    async def run_one(task_id: str, fn: Callable, args: tuple, kwargs: dict) -> None:
        async with sem:
            try:
                if timeout:
                    result = await asyncio.wait_for(fn(*args, **kwargs), timeout=timeout)
                else:
                    result = await fn(*args, **kwargs)
                results[task_id] = result
            except Exception as exc:
                errors[task_id] = str(exc)

    await asyncio.gather(*[
        run_one(tid, fn, args, kwargs)
        for tid, fn, args, kwargs in tasks
    ])
    return {"results": results, "errors": errors}


async def map_parallel(
    items: list[Any],
    fn: Callable[[Any], Awaitable[Any]],
    concurrency: int = 5,
) -> list[Any | None]:
    sem = asyncio.Semaphore(concurrency)
    results: list[Any | None] = [None] * len(items)

    async def process(i: int, item: Any) -> None:
        async with sem:
            try:
                results[i] = await fn(item)
            except Exception:
                results[i] = None

    await asyncio.gather(*[process(i, item) for i, item in enumerate(items)])
    return results
