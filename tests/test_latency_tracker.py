from __future__ import annotations
import time
from research_agent.latency_tracker import LatencyTracker


def test_context_manager_records():
    lt = LatencyTracker()
    with lt.track("retrieval"):
        time.sleep(0.005)
    assert lt.mean("retrieval") >= 5.0


def test_manual_record():
    lt = LatencyTracker()
    lt.record("synthesis", 100.0)
    lt.record("synthesis", 200.0)
    assert lt.mean("synthesis") == 150.0


def test_p99():
    lt = LatencyTracker()
    for i in range(1, 101):
        lt.record("op", float(i))
    assert lt.p99("op") >= 99.0


def test_summary_keys():
    lt = LatencyTracker()
    lt.record("x", 10.0)
    s = lt.summary("x")
    assert all(k in s for k in ("name", "count", "mean_ms", "p99_ms"))
