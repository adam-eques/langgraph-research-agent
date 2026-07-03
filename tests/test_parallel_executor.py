from __future__ import annotations

import asyncio

from research_agent.parallel_executor import map_parallel, run_parallel


async def double(x: int) -> int:
    return x * 2


def test_run_parallel_basic():
    tasks = [("t1", double, (5,), {}), ("t2", double, (10,), {})]
    out = asyncio.run(run_parallel(tasks))
    assert out["results"]["t1"] == 10 and out["results"]["t2"] == 20


def test_run_parallel_captures_error():
    async def fail():
        raise ValueError("boom")

    tasks = [("bad", fail, (), {})]
    out = asyncio.run(run_parallel(tasks))
    assert "bad" in out["errors"]


def test_map_parallel():
    result = asyncio.run(map_parallel([1, 2, 3], double))
    assert result == [2, 4, 6]


def test_map_parallel_handles_error():
    async def failing(x):
        raise RuntimeError("err")

    result = asyncio.run(map_parallel([1, 2], failing))
    assert all(r is None for r in result)
