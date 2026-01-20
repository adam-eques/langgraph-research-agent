from __future__ import annotations
import asyncio
from research_agent.task_queue import AsyncTaskQueue, TaskPriority


async def add_one(x: int) -> int:
    return x + 1


def test_submit_and_result():
    async def run():
        q = AsyncTaskQueue(workers=2)
        await q.submit("t1", add_one, 5)
        await q.run_until_empty()
        return q.get_result("t1")
    assert asyncio.run(run()) == 6


def test_multiple_tasks():
    async def run():
        q = AsyncTaskQueue(workers=3)
        for i in range(5):
            await q.submit(f"t{i}", add_one, i)
        await q.run_until_empty()
        return [q.get_result(f"t{i}") for i in range(5)]
    results = asyncio.run(run())
    assert results == [1, 2, 3, 4, 5]


def test_error_captured():
    async def fail():
        raise RuntimeError("boom")

    async def run():
        q = AsyncTaskQueue(workers=1)
        await q.submit("bad", fail)
        await q.run_until_empty()
        return q.get_error("bad")
    err = asyncio.run(run())
    assert isinstance(err, RuntimeError)
