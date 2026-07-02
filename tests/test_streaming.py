"""Tests for sync and async streaming functions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_chunk(node: str, content: str) -> tuple[str, list]:
    chunk = AIMessageChunk(content=content)
    return (node, [chunk])


def _base_initial():
    return {
        "messages": [],
        "query": "test query",
        "research_notes": [],
        "document_context": "",
        "citations": [],
        "next": "",
    }


# ---------------------------------------------------------------------------
# sync stream_tokens
# ---------------------------------------------------------------------------


class TestStreamTokens:
    @patch("research_agent.streaming.build_graph")
    def test_yields_synthesizer_tokens(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter(
            [
                ("retriever", [AIMessageChunk(content="")]),
                ("synthesizer", [AIMessageChunk(content="Hello")]),
                ("synthesizer", [AIMessageChunk(content=" world")]),
            ]
        )
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import stream_tokens

        tokens = list(stream_tokens("test query"))

        assert tokens == ["Hello", " world"]

    @patch("research_agent.streaming.build_graph")
    def test_skips_non_synthesizer_nodes(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter(
            [
                ("researcher", [AIMessageChunk(content="research data")]),
                ("analyst", [AIMessageChunk(content="analysis data")]),
                ("synthesizer", [AIMessageChunk(content="final answer")]),
            ]
        )
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import stream_tokens

        tokens = list(stream_tokens("query"))

        assert tokens == ["final answer"]
        assert "research data" not in tokens
        assert "analysis data" not in tokens

    @patch("research_agent.streaming.build_graph")
    def test_returns_empty_when_no_synthesizer(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter(
            [
                ("researcher", [AIMessageChunk(content="data")]),
            ]
        )
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import stream_tokens

        tokens = list(stream_tokens("query"))

        assert tokens == []

    @patch("research_agent.streaming.build_graph")
    def test_skips_empty_content_chunks(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.stream.return_value = iter(
            [
                ("synthesizer", [AIMessageChunk(content="")]),
                ("synthesizer", [AIMessageChunk(content="real content")]),
                ("synthesizer", [AIMessageChunk(content="")]),
            ]
        )
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import stream_tokens

        tokens = list(stream_tokens("query"))

        # Only non-empty tokens
        assert all(t for t in tokens)
        assert "real content" in tokens


# ---------------------------------------------------------------------------
# async astream_tokens
# ---------------------------------------------------------------------------


class TestAstreamTokens:
    @pytest.mark.asyncio
    @patch("research_agent.streaming.build_graph")
    async def test_async_yields_synthesizer_tokens(self, mock_build_graph):
        async def _fake_astream(*args, **kwargs):
            for item in [
                ("retriever", [AIMessageChunk(content="retriever output")]),
                ("synthesizer", [AIMessageChunk(content="async token 1")]),
                ("synthesizer", [AIMessageChunk(content=" async token 2")]),
            ]:
                yield item

        mock_graph = MagicMock()
        mock_graph.astream = _fake_astream
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import astream_tokens

        tokens = []
        async for token in astream_tokens("async query"):
            tokens.append(token)

        assert tokens == ["async token 1", " async token 2"]

    @pytest.mark.asyncio
    @patch("research_agent.streaming.build_graph")
    async def test_async_handles_empty_stream(self, mock_build_graph):
        async def _empty_astream(*args, **kwargs):
            return
            yield  # make it an async generator

        mock_graph = MagicMock()
        mock_graph.astream = _empty_astream
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import astream_tokens

        tokens = []
        async for token in astream_tokens("query"):
            tokens.append(token)

        assert tokens == []


# ---------------------------------------------------------------------------
# run() function
# ---------------------------------------------------------------------------


class TestRun:
    @patch("research_agent.streaming.build_graph")
    def test_run_returns_state_dict(self, mock_build_graph):
        expected_state = {
            "messages": [AIMessage(content="The answer")],
            "query": "test",
            "research_notes": ["note 1"],
            "document_context": "",
            "citations": [],
            "next": "end",
        }
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = expected_state
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import run

        result = run("test")

        assert result["query"] == "test"
        assert result["research_notes"] == ["note 1"]

    @patch("research_agent.streaming.build_graph")
    def test_run_passes_correct_initial_state(self, mock_build_graph):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "messages": [],
            "query": "q",
            "research_notes": [],
            "document_context": "",
            "citations": [],
            "next": "",
        }
        mock_build_graph.return_value = mock_graph

        from research_agent.streaming import run

        run("my research query")

        call_args = mock_graph.invoke.call_args[0][0]
        assert call_args["query"] == "my research query"
        assert call_args["messages"] == []
        assert call_args["research_notes"] == []
