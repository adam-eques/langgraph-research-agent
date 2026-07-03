from __future__ import annotations

import time

from research_agent.cache_invalidator import CacheInvalidator


def test_register_and_invalidate():
    ci = CacheInvalidator()
    ci.register("key1")
    assert ci.invalidate("key1") is True and len(ci) == 0


def test_invalidate_by_tag():
    ci = CacheInvalidator()
    ci.register("k1", tags=["search"])
    ci.register("k2", tags=["search"])
    ci.register("k3", tags=["rag"])
    assert ci.invalidate_by_tag("search") == 2 and len(ci) == 1


def test_invalidate_older_than():
    ci = CacheInvalidator()
    ci.register("old")
    time.sleep(0.01)
    count = ci.invalidate_older_than(max_age_seconds=0.005)
    assert count == 1


def test_missing_key_returns_false():
    ci = CacheInvalidator()
    assert ci.invalidate("nonexistent") is False
