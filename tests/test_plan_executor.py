from __future__ import annotations

import asyncio
import pytest
from research_agent.plan_executor import PlanExecutor


@pytest.mark.asyncio
async def test_sequential_execution():
    async def search(q):
        return f"result:{q}"
    executor = PlanExecutor(search_fn=search)
    results = await executor.execute_sequential(["q1", "q2"])
    assert len(results) == 2
    assert all(r["ok"] for r in results)


@pytest.mark.asyncio
async def test_parallel_execution():
    async def search(q):
        return f"r:{q}"
    executor = PlanExecutor(search_fn=search, concurrency=2)
    results = await executor.execute_parallel(["a", "b", "c"])
    assert len(results) == 3


@pytest.mark.asyncio
async def test_handles_failure():
    async def search(q):
        raise RuntimeError("fail")
    executor = PlanExecutor(search_fn=search)
    results = await executor.execute_sequential(["q1"])
    assert results[0]["ok"] is False
