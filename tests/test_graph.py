from __future__ import annotations

import pytest

from research_agent.graph import build_graph


def test_build_graph_returns_compiled():
    graph = build_graph()
    assert graph is not None


def test_build_graph_with_checkpointing():
    graph = build_graph(checkpointing=True)
    assert graph is not None


def test_graph_nodes_present():
    graph = build_graph()
    nodes = set(graph.get_graph().nodes.keys())
    assert "retriever" in nodes
    assert "researcher" in nodes
    assert "analyst" in nodes
    assert "synthesizer" in nodes


@pytest.mark.asyncio
async def test_graph_async_stream_returns_iterator():
    graph = build_graph()
    # Verify the async stream interface exists without running a full API call
    assert hasattr(graph, "astream")
