from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class StreamWriter:
    def __init__(self, buffer_size: int = 32) -> None:
        self._queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=buffer_size)
        self._closed = False
        self._total_written = 0

    async def write(self, chunk: str) -> None:
        if self._closed:
            raise RuntimeError("StreamWriter is closed")
        await self._queue.put(chunk)
        self._total_written += len(chunk)

    async def close(self) -> None:
        self._closed = True
        await self._queue.put(None)

    async def __aiter__(self) -> AsyncIterator[str]:
        while True:
            chunk = await self._queue.get()
            if chunk is None:
                break
            yield chunk
            self._queue.task_done()

    @property
    def total_written(self) -> int:
        return self._total_written


async def stream_to_string(writer: StreamWriter) -> str:
    parts = []
    async for chunk in writer:
        parts.append(chunk)
    return "".join(parts)


async def write_chunks(writer: StreamWriter, chunks: list[str], delay: float = 0.0) -> None:
    for chunk in chunks:
        await writer.write(chunk)
        if delay:
            await asyncio.sleep(delay)
    await writer.close()
