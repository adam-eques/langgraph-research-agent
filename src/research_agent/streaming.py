from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, cast

from langchain_core.messages import AIMessageChunk

from research_agent.graph import build_graph
from research_agent.state import ResearchState


def run(query: str, **kwargs: Any) -> ResearchState:
    graph = build_graph()
    initial: ResearchState = {
        "messages": [],
        "query": query,
        "research_notes": [],
        "document_context": "",
        "next": "",
    }
    return cast(ResearchState, graph.invoke(initial, **kwargs))


def stream_tokens(query: str) -> Iterator[str]:
    """Yield text tokens as they arrive from the synthesizer node."""
    graph = build_graph()
    initial: ResearchState = {
        "messages": [],
        "query": query,
        "research_notes": [],
        "document_context": "",
        "next": "",
    }
    for chunk in graph.stream(initial, stream_mode="messages"):
        node, messages = chunk if isinstance(chunk, tuple) else (None, chunk)
        if node == "synthesizer":
            for msg in messages if isinstance(messages, list) else [messages]:
                if isinstance(msg, AIMessageChunk) and msg.content:
                    yield str(msg.content)


async def astream_tokens(query: str) -> AsyncIterator[str]:
    """Async token streaming from the synthesizer node."""
    graph = build_graph()
    initial: ResearchState = {
        "messages": [],
        "query": query,
        "research_notes": [],
        "document_context": "",
        "next": "",
    }
    async for chunk in graph.astream(initial, stream_mode="messages"):
        node, messages = chunk if isinstance(chunk, tuple) else (None, chunk)
        if node == "synthesizer":
            for msg in messages if isinstance(messages, list) else [messages]:
                if isinstance(msg, AIMessageChunk) and msg.content:
                    yield str(msg.content)
