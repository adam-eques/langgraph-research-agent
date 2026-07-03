from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

logger = logging.getLogger(__name__)


class StreamAggregator:
    """Merge multiple async streams into one ordered stream."""

    def __init__(self) -> None:
        self._streams: list[AsyncIterator[Any]] = []

    def add(self, stream: AsyncIterator[Any]) -> StreamAggregator:
        self._streams.append(stream)
        return self

    async def __aiter__(self) -> AsyncIterator[Any]:
        queue: asyncio.Queue = asyncio.Queue()
        done_count = 0
        total = len(self._streams)

        async def drain(stream: AsyncIterator) -> None:
            nonlocal done_count
            async for item in stream:
                await queue.put(item)
            done_count += 1
            if done_count == total:
                await queue.put(None)

        tasks = [asyncio.create_task(drain(s)) for s in self._streams]
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
        for t in tasks:
            t.cancel()
