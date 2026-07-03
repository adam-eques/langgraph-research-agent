from __future__ import annotations

import time

from research_agent.response_cache import ResponseCache


def test_set_and_get():
    rc = ResponseCache(ttl=60)
    rc.set("What is AI?", {"text": "AI is..."})
    assert rc.get("What is AI?")["text"] == "AI is..."


def test_model_key_isolation():
    rc = ResponseCache(ttl=60)
    rc.set("Q", "resp-a", model="claude")
    rc.set("Q", "resp-b", model="gpt")
    assert rc.get("Q", "claude") != rc.get("Q", "gpt")


def test_ttl_expiry():
    rc = ResponseCache(ttl=0.001)
    rc.set("Q", "R")
    time.sleep(0.01)
    assert rc.get("Q") is None


def test_max_entries_evicts():
    rc = ResponseCache(ttl=60, max_entries=2)
    rc.set("A", 1)
    rc.set("B", 2)
    rc.set("C", 3)
    assert rc.size == 2
