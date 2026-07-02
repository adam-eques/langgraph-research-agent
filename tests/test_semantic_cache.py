from __future__ import annotations

from research_agent.semantic_cache import SemanticCache


def test_set_and_get():
    cache = SemanticCache()
    cache.set("What is AI?", {"answer": "AI is..."})
    result = cache.get("What is AI?")
    assert result is not None
    assert result["answer"] == "AI is..."


def test_normalized_key_matches():
    cache = SemanticCache()
    cache.set("  what is AI?  ", "result")
    assert cache.get("what is AI?") == "result"


def test_lru_eviction():
    cache = SemanticCache(max_size=2)
    cache.set("q1", 1)
    cache.set("q2", 2)
    cache.set("q3", 3)
    assert cache.size == 2
    assert cache.get("q1") is None


def test_invalidate():
    cache = SemanticCache()
    cache.set("q", "v")
    assert cache.invalidate("q") is True
    assert cache.get("q") is None


def test_clear():
    cache = SemanticCache()
    cache.set("a", 1)
    cache.clear()
    assert cache.size == 0
