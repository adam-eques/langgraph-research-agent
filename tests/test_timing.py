from __future__ import annotations

import asyncio

from research_agent.timing import async_timed, timed


def test_timed_returns_result():
    @timed("test_fn")
    def fn():
        return 42

    assert fn() == 42


def test_timed_does_not_raise():
    @timed()
    def fn():
        return "ok"

    assert fn() == "ok"


def test_async_timed_returns_result():
    @async_timed("async_fn")
    async def fn():
        return "async_result"

    result = asyncio.run(fn())
    assert result == "async_result"
