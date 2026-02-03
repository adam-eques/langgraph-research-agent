from __future__ import annotations

import asyncio
import pytest
from research_agent.node_timeout import with_timeout


@pytest.mark.asyncio
async def test_completes_within_timeout():
    @with_timeout(1.0, "fast_node")
    async def fn():
        return "done"
    assert await fn() == "done"


@pytest.mark.asyncio
async def test_raises_on_timeout():
    @with_timeout(0.05, "slow_node")
    async def fn():
        await asyncio.sleep(1.0)
        return "never"
    with pytest.raises(asyncio.TimeoutError):
        await fn()
