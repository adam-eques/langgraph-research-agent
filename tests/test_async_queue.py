from __future__ import annotations

import pytest

from research_agent.async_queue import AsyncQueue


@pytest.mark.asyncio
async def test_put_and_get():
    q = AsyncQueue()
    await q.put("hello")
    result = await q.get()
    assert result == "hello"


@pytest.mark.asyncio
async def test_async_iter():
    q = AsyncQueue()
    await q.put(1)
    await q.put(2)
    q.done()
    items = []
    async for item in q:
        items.append(item)
    assert set(items) == {1, 2}
