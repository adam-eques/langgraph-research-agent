from __future__ import annotations

import pytest

from research_agent.cache import ResultCache


@pytest.fixture
def cache():
    return ResultCache(max_size=10)


def test_set_and_get(cache):
    cache.set("hello world", {"answer": "42"})
    result = cache.get("hello world")
    assert result == {"answer": "42"}


def test_get_missing_returns_none(cache):
    assert cache.get("nonexistent query") is None


def test_cache_is_case_insensitive_via_hash(cache):
    cache.set("Hello World", {"answer": "a"})
    # Same normalized key
    assert cache.get("hello world") == {"answer": "a"}


def test_invalidate_removes_entry(cache):
    cache.set("my query", {"data": 1})
    cache.invalidate("my query")
    assert cache.get("my query") is None


def test_invalidate_nonexistent_does_not_raise(cache):
    cache.invalidate("nonexistent")  # should not raise


def test_lru_eviction(cache):
    for i in range(12):  # exceeds max_size=10
        cache.set(f"query {i}", {"i": i})
    # Oldest entries should be evicted
    total_hits = sum(1 for i in range(12) if cache.get(f"query {i}") is not None)
    assert total_hits <= 10


def test_overwrite_existing(cache):
    cache.set("q", {"v": 1})
    cache.set("q", {"v": 2})
    assert cache.get("q") == {"v": 2}
