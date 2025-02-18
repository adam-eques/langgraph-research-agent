"""Tests for ConversationMemory in-memory backend."""
from __future__ import annotations

import time

import pytest

from research_agent.memory import ConversationMemory, _InMemoryBackend


# ---------------------------------------------------------------------------
# _InMemoryBackend
# ---------------------------------------------------------------------------

class TestInMemoryBackend:
    def setup_method(self):
        self.backend = _InMemoryBackend()

    def test_save_and_retrieve_single_turn(self):
        self.backend.save_turn("s1", "What is AI?", "AI is artificial intelligence.")
        history = self.backend.get_history("s1")
        assert len(history) == 1
        assert history[0]["query"] == "What is AI?"
        assert history[0]["response"] == "AI is artificial intelligence."
        assert "timestamp" in history[0]

    def test_multiple_turns_ordered_chronologically(self):
        self.backend.save_turn("s2", "Q1", "A1")
        self.backend.save_turn("s2", "Q2", "A2")
        self.backend.save_turn("s2", "Q3", "A3")

        history = self.backend.get_history("s2")
        assert [h["query"] for h in history] == ["Q1", "Q2", "Q3"]

    def test_max_turns_limits_history(self):
        for i in range(20):
            self.backend.save_turn("s3", f"Q{i}", f"A{i}")

        history = self.backend.get_history("s3", max_turns=5)
        assert len(history) == 5
        # Should return the LAST 5 turns
        assert history[-1]["query"] == "Q19"
        assert history[0]["query"] == "Q15"

    def test_clear_removes_session(self):
        self.backend.save_turn("s4", "Q", "A")
        self.backend.clear("s4")
        history = self.backend.get_history("s4")
        assert history == []

    def test_clear_nonexistent_session_is_safe(self):
        # Should not raise
        self.backend.clear("does-not-exist")

    def test_isolated_sessions(self):
        self.backend.save_turn("sessA", "A query", "A response")
        self.backend.save_turn("sessB", "B query", "B response")

        histA = self.backend.get_history("sessA")
        histB = self.backend.get_history("sessB")

        assert len(histA) == 1
        assert len(histB) == 1
        assert histA[0]["query"] == "A query"
        assert histB[0]["query"] == "B query"

    def test_empty_session_returns_empty_list(self):
        history = self.backend.get_history("nonexistent")
        assert history == []

    def test_timestamp_is_recent(self):
        before = time.time()
        self.backend.save_turn("s5", "Q", "A")
        after = time.time()

        history = self.backend.get_history("s5")
        ts = history[0]["timestamp"]
        assert before <= ts <= after


# ---------------------------------------------------------------------------
# ConversationMemory (integration via env var)
# ---------------------------------------------------------------------------

class TestConversationMemory:
    def setup_method(self):
        """Ensure we always use the in-memory backend."""
        import os
        os.environ["MEMORY_BACKEND"] = "memory"
        self.memory = ConversationMemory()

    def test_save_and_get_history(self):
        self.memory.save_turn("test-session", "Hello", "Hi there!")
        history = self.memory.get_history("test-session")
        assert len(history) == 1
        assert history[0]["query"] == "Hello"

    def test_clear_session(self):
        self.memory.save_turn("test-session-2", "Q", "A")
        self.memory.clear("test-session-2")
        assert self.memory.get_history("test-session-2") == []

    def test_format_as_context_empty(self):
        ctx = self.memory.format_as_context("empty-session")
        assert ctx == ""

    def test_format_as_context_with_turns(self):
        self.memory.save_turn("fmt-session", "What is ML?", "Machine learning is ...")
        self.memory.save_turn("fmt-session", "How does it work?", "It uses data ...")

        ctx = self.memory.format_as_context("fmt-session")
        assert "What is ML?" in ctx
        assert "Machine learning is ..." in ctx
        assert "How does it work?" in ctx

    def test_format_as_context_max_turns(self):
        for i in range(10):
            self.memory.save_turn("max-session", f"Q{i}", f"A{i}")

        ctx = self.memory.format_as_context("max-session", max_turns=2)
        # Only last 2 turns should appear
        assert "Q8" in ctx
        assert "Q9" in ctx
        assert "Q0" not in ctx

    def test_max_turns_respected(self):
        for i in range(15):
            self.memory.save_turn("many-turns", f"Q{i}", f"A{i}")

        history = self.memory.get_history("many-turns", max_turns=3)
        assert len(history) == 3
