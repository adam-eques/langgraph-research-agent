from __future__ import annotations

import asyncio
import pytest
from research_agent.backoff import call_with_backoff


@pytest.mark.asyncio
async def test_succeeds_first_attempt():
    calls = []
    async def fn():
        calls.append(1)
        return "ok"
    result = await call_with_backoff(fn, max_attempts=3, base_delay=0)
    assert result == "ok"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_retries_on_failure():
    calls = []
    async def fn():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("fail")
        return "recovered"
    result = await call_with_backoff(fn, max_attempts=4, base_delay=0)
    assert result == "recovered"
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_raises_after_max_attempts():
    async def fn():
        raise RuntimeError("always fails")
    with pytest.raises(RuntimeError, match="All 3 attempts failed"):
        await call_with_backoff(fn, max_attempts=3, base_delay=0)
