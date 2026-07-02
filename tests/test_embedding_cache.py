from __future__ import annotations

from research_agent.rag.embedding_cache import EmbeddingCache


def test_set_and_get():
    cache = EmbeddingCache()
    cache.set("hello world", [0.1, 0.2, 0.3])
    assert cache.get("hello world") == [0.1, 0.2, 0.3]


def test_cache_miss():
    assert EmbeddingCache().get("not cached") is None


def test_lru_eviction():
    cache = EmbeddingCache(max_size=2)
    cache.set("a", [1.0])
    cache.set("b", [2.0])
    cache.set("c", [3.0])
    assert len(cache) == 2 and cache.get("a") is None
