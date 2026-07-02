from __future__ import annotations
from research_agent.retrieval_cache import RetrievalCache


def test_set_and_get():
    rc = RetrievalCache(ttl=60)
    rc.set("AI", [{"text": "doc1"}])
    assert rc.get("AI") == [{"text": "doc1"}]


def test_miss():
    rc = RetrievalCache(ttl=60)
    assert rc.get("missing") is None


def test_ttl_expired():
    rc = RetrievalCache(ttl=0.001)
    rc.set("AI", ["doc"])
    import time; time.sleep(0.01)
    assert rc.get("AI") is None


def test_invalidate():
    rc = RetrievalCache(ttl=60)
    rc.set("q", ["r"])
    assert rc.invalidate("q") is True and rc.get("q") is None


def test_max_size_evicts():
    rc = RetrievalCache(ttl=60, max_size=2)
    rc.set("a", [1]); rc.set("b", [2]); rc.set("c", [3])
    assert rc.size == 2
