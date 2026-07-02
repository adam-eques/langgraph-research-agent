from __future__ import annotations

import asyncio

from research_agent.search_client import MockSearchClient, SearchClientPool


def test_mock_returns_results():
    client = MockSearchClient()
    results = asyncio.run(client.search("AI", num_results=3))
    assert len(results) == 3 and all(r.url for r in results)


def test_mock_result_titles_contain_query():
    client = MockSearchClient()
    results = asyncio.run(client.search("LangGraph"))
    assert all("LangGraph" in r.title for r in results)


def test_pool_aggregates():
    clients = [MockSearchClient(), MockSearchClient()]
    pool = SearchClientPool(clients, concurrency=2)
    results = asyncio.run(pool.search_all("test", num_results=2))
    assert len(results) == 4
