from __future__ import annotations

import pytest

from research_agent.streaming_parser import collect_stream


@pytest.mark.asyncio
async def test_collect_stream_from_dicts():
    async def gen():
        for text in ["hello", " ", "world"]:
            yield {"content": text}

    result = await collect_stream(gen())
    assert result == "hello world"


@pytest.mark.asyncio
async def test_collect_stream_skips_empty():
    async def gen():
        yield {"content": ""}
        yield {"content": "data"}

    result = await collect_stream(gen())
    assert result == "data"
