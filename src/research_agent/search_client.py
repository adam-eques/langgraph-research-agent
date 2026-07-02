from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import cast

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    rank: int = 0


class MockSearchClient:
    def __init__(self, delay: float = 0.0) -> None:
        self._delay = delay

    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        if self._delay:
            await asyncio.sleep(self._delay)
        return [
            SearchResult(
                title=f"Result {i + 1} for '{query}'",
                url=f"https://example.com/{i + 1}",
                snippet=f"This is a mock snippet about {query} result {i + 1}.",
                rank=i,
            )
            for i in range(num_results)
        ]


class SearchClientPool:
    def __init__(self, clients: list, concurrency: int = 3) -> None:
        self._clients = clients
        self._sem = asyncio.Semaphore(concurrency)

    async def search_all(self, query: str, num_results: int = 5) -> list[SearchResult]:
        async def _search(client) -> list[SearchResult]:
            async with self._sem:
                return cast(list[SearchResult], await client.search(query, num_results))

        results = await asyncio.gather(*[_search(c) for c in self._clients], return_exceptions=True)
        merged = []
        for r in results:
            if isinstance(r, list):
                merged.extend(r)
        return merged
