"""Integration tests — require real API keys. Skip in CI by default."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping integration tests",
)


@pytest.mark.integration
def test_build_graph_compiles():
    """Graph should compile without errors."""
    from research_agent.graph import build_graph

    graph = build_graph()
    assert graph is not None


@pytest.mark.integration
def test_build_graph_nodes():
    from research_agent.graph import build_graph

    graph = build_graph()
    nodes = set(graph.get_graph().nodes.keys())
    expected = {"retriever", "researcher", "research_tools", "analyst", "synthesizer"}
    assert expected.issubset(nodes)


@pytest.mark.integration
def test_supervisor_graph_compiles():
    from research_agent.graph import build_graph

    graph = build_graph(use_supervisor=True)
    nodes = set(graph.get_graph().nodes.keys())
    assert "supervisor" in nodes
