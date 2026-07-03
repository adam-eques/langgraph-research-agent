"""Tests for BatchProcessor with mocked research pipeline."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage

from research_agent.batch import BatchProcessor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_state(query: str, answer: str = "Test answer") -> dict:
    return {
        "messages": [AIMessage(content=answer)],
        "query": query,
        "research_notes": ["Note 1"],
        "citations": [],
        "document_context": "",
        "next": "end",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBatchProcessor:
    @pytest.mark.asyncio
    @patch("research_agent.batch.BatchProcessor._run_single")
    async def test_processes_all_queries(self, mock_run_single):
        async def _fake_run(query: str) -> dict:
            return {
                "query": query,
                "answer": f"Answer to: {query}",
                "research_notes": [],
                "citations": [],
                "error": None,
            }

        mock_run_single.side_effect = _fake_run

        processor = BatchProcessor()
        queries = ["Q1", "Q2", "Q3"]
        results = await processor.process_batch(queries)

        assert len(results) == 3
        assert {r["query"] for r in results} == set(queries)

    @pytest.mark.asyncio
    @patch("research_agent.batch.BatchProcessor._run_single")
    async def test_returns_error_on_failure(self, mock_run_single):
        async def _fail(query: str) -> dict:
            return {
                "query": query,
                "answer": "",
                "research_notes": [],
                "citations": [],
                "error": "Connection refused",
            }

        mock_run_single.side_effect = _fail

        processor = BatchProcessor()
        results = await processor.process_batch(["bad query"])

        assert results[0]["error"] == "Connection refused"
        assert results[0]["answer"] == ""

    @pytest.mark.asyncio
    @patch("research_agent.batch.BatchProcessor._run_single")
    async def test_respects_max_concurrent(self, mock_run_single):
        """Verify that max_concurrent=2 means at most 2 queries run at once."""
        active_count = [0]
        max_active = [0]

        async def _slow_run(query: str) -> dict:
            active_count[0] += 1
            max_active[0] = max(max_active[0], active_count[0])
            await asyncio.sleep(0.05)  # simulate work
            active_count[0] -= 1
            return {
                "query": query,
                "answer": "ok",
                "research_notes": [],
                "citations": [],
                "error": None,
            }

        mock_run_single.side_effect = _slow_run

        processor = BatchProcessor()
        queries = [f"Q{i}" for i in range(6)]
        await processor.process_batch(queries, max_concurrent=2)

        assert max_active[0] <= 2

    @pytest.mark.asyncio
    async def test_empty_queries_returns_empty(self):
        processor = BatchProcessor()
        results = await processor.process_batch([])
        assert results == []

    @pytest.mark.asyncio
    @patch("research_agent.batch.BatchProcessor._run_single")
    async def test_on_complete_callback_called(self, mock_run_single):
        async def _ok(query: str) -> dict:
            return {
                "query": query,
                "answer": "a",
                "research_notes": [],
                "citations": [],
                "error": None,
            }

        mock_run_single.side_effect = _ok

        completed_calls: list[tuple[int, int]] = []

        def on_complete(done: int, total: int) -> None:
            completed_calls.append((done, total))

        processor = BatchProcessor(on_complete=on_complete)
        queries = ["Q1", "Q2", "Q3"]
        await processor.process_batch(queries)

        assert len(completed_calls) == 3
        totals = {t for _, t in completed_calls}
        assert totals == {3}
        done_counts = sorted(d for d, _ in completed_calls)
        assert done_counts == [1, 2, 3]

    @pytest.mark.asyncio
    @patch("research_agent.batch.BatchProcessor._run_single")
    async def test_result_contains_duration(self, mock_run_single):
        async def _timed(query: str) -> dict:
            return {
                "query": query,
                "answer": "a",
                "research_notes": [],
                "citations": [],
                "error": None,
            }

        mock_run_single.side_effect = _timed

        processor = BatchProcessor()
        results = await processor.process_batch(["query"], max_concurrent=1)

        assert "duration_seconds" in results[0]
        assert isinstance(results[0]["duration_seconds"], float)
        assert results[0]["duration_seconds"] >= 0

    @pytest.mark.asyncio
    @patch("research_agent.streaming.run")
    async def test_run_single_handles_real_pipeline_mock(self, mock_run):
        mock_run.return_value = {
            "messages": [AIMessage(content="Mocked answer")],
            "query": "test",
            "research_notes": ["note"],
            "citations": [{"source": "doc.pdf", "excerpt": "...", "relevance": "high"}],
            "document_context": "",
            "next": "end",
        }

        processor = BatchProcessor()
        result = await processor._run_single("test query")

        assert result["answer"] == "Mocked answer"
        assert result["research_notes"] == ["note"]
        assert result["error"] is None
