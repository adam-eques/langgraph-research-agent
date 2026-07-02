from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any


class AsyncQueue:
    def __init__(self, maxsize: int = 0) -> None:
        self._q: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._done = False

    async def put(self, item: Any) -> None:
        await self._q.put(item)

    async def get(self) -> Any:
        return await self._q.get()

    def done(self) -> None:
        self._done = True

    async def __aiter__(self) -> AsyncIterator[Any]:
        while not self._done or not self._q.empty():
            try:
                item = await asyncio.wait_for(self._q.get(), timeout=0.05)
                yield item
            except TimeoutError:
                continue
