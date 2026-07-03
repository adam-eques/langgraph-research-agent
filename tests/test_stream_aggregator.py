from __future__ import annotations

import pytest

from research_agent.stream_aggregator import StreamAggregator


async def make_stream(items):
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_single_stream():
    agg = StreamAggregator()
    agg.add(make_stream([1, 2, 3]))
    result = []
    async for item in agg:
        result.append(item)
    assert sorted(result) == [1, 2, 3]


@pytest.mark.asyncio
async def test_two_streams():
    agg = StreamAggregator()
    agg.add(make_stream(["a", "b"]))
    agg.add(make_stream(["c", "d"]))
    result = []
    async for item in agg:
        result.append(item)
    assert set(result) == {"a", "b", "c", "d"}
