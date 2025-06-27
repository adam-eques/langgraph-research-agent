from __future__ import annotations

from research_agent.profiler import GraphProfiler


def test_record_and_report():
    p = GraphProfiler()
    p.record_call("retriever", 50.0)
    p.record_call("retriever", 30.0)
    report = p.report()
    assert report["retriever"]["calls"] == 2
    assert report["retriever"]["avg_ms"] == 40.0


def test_error_tracking():
    p = GraphProfiler()
    p.record_call("researcher", 100.0, error=True)
    assert p.report()["researcher"]["errors"] == 1


def test_slowest_node():
    p = GraphProfiler()
    p.record_call("fast", 10.0)
    p.record_call("slow", 200.0)
    assert p.slowest_node() == "slow"


def test_empty_profiler():
    p = GraphProfiler()
    assert p.slowest_node() is None
    assert p.report() == {}
