from __future__ import annotations

import asyncio

from research_agent.batch_processor import process_batch


async def square(x: int) -> int:
    return x * x


async def fail_on_even(x: int) -> int:
    if x % 2 == 0:
        raise ValueError(f"even: {x}")
    return x


def test_batch_all_succeed():
    result = asyncio.run(process_batch([1, 2, 3, 4, 5], square))
    assert result.succeeded == 5 and result.results == [1, 4, 9, 16, 25]


def test_batch_partial_failure():
    result = asyncio.run(process_batch([1, 2, 3], fail_on_even))
    assert result.succeeded == 2 and result.failed == 1


def test_success_rate():
    result = asyncio.run(process_batch([1, 2], fail_on_even))
    assert 0.0 <= result.success_rate <= 1.0
