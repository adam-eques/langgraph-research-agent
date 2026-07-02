from __future__ import annotations

from research_agent.answer_cache import AnswerCache


def test_set_and_get(tmp_path):
    cache = AnswerCache(str(tmp_path / "cache.json"))
    cache.set("What is AI?", {"answer": "AI is..."})
    assert cache.get("What is AI?")["answer"] == "AI is..."


def test_cache_miss(tmp_path):
    assert AnswerCache(str(tmp_path / "c.json")).get("unknown") is None


def test_invalidate(tmp_path):
    cache = AnswerCache(str(tmp_path / "cache.json"))
    cache.set("q", {"a": 1})
    assert cache.invalidate("q") is True
    assert cache.get("q") is None


def test_size(tmp_path):
    cache = AnswerCache(str(tmp_path / "cache.json"))
    cache.set("q1", {})
    cache.set("q2", {})
    assert cache.size == 2
