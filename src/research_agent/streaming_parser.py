from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

logger = logging.getLogger(__name__)


async def parse_stream_chunks(
    stream: AsyncIterator[Any],
    text_key: str = "content",
) -> AsyncIterator[str]:
    """Extract text from async stream of LangChain chunks."""
    async for chunk in stream:
        if hasattr(chunk, text_key):
            val = getattr(chunk, text_key)
            if isinstance(val, str) and val:
                yield val
        elif isinstance(chunk, dict) and text_key in chunk:
            val = chunk[text_key]
            if isinstance(val, str) and val:
                yield val


async def collect_stream(stream: AsyncIterator[Any], text_key: str = "content") -> str:
    """Collect all text chunks from a stream into a single string."""
    parts = []
    async for chunk in parse_stream_chunks(stream, text_key=text_key):
        parts.append(chunk)
    return "".join(parts)
