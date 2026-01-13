from __future__ import annotations

import asyncio
import pytest
from research_agent.multi_query import run_multi_query, deduplicate_results


@pytest.mark.asyncio
async def test_run_multi_query_success():
    async def fake_search(q):
        return f"result for {q}"
    results = await run_multi_query(["q1", "q2"], fake_search, concurrency=2)
    assert len(results) == 2
    assert all(r["error"] is None for r in results)


@pytest.mark.asyncio
async def test_run_multi_query_handles_error():
    async def failing_search(q):
        raise RuntimeError("search failed")
    results = await run_multi_query(["q1"], failing_search)
    assert results[0]["error"] is not None


def test_deduplicate_results():
    results = [
        {"query": "What is AI?", "result": "r1"},
        {"query": "what is ai?", "result": "r2"},
    ]
    unique = deduplicate_results(results)
    assert len(unique) == 1
