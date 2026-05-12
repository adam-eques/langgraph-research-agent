from __future__ import annotations

import asyncio
import pytest
from research_agent.query_cache_warmer import QueryCacheWarmer
from research_agent.semantic_cache import SemanticCache


@pytest.mark.asyncio
async def test_warms_cache():
    cache = SemanticCache()
    async def search(q):
        return f"result:{q}"
    warmer = QueryCacheWarmer(search_fn=search, cache=cache)
    results = await warmer.warm(["What is AI?"])
    assert results["What is AI?"] is True
    assert cache.get("What is AI?") is not None


@pytest.mark.asyncio
async def test_skips_already_warm():
    cache = SemanticCache()
    cache.set("known query", "cached")
    async def search(q):
        return "fresh"
    warmer = QueryCacheWarmer(search_fn=search, cache=cache)
    results = await warmer.warm(["known query"])
    assert results["known query"] is False
