from __future__ import annotations
from research_agent.metric_tracker import MetricTracker


def test_counter():
    mt = MetricTracker()
    mt.increment("req"); mt.increment("req", 3)
    assert mt.counter("req") == 4.0


def test_gauge():
    mt = MetricTracker()
    mt.gauge("cpu", 0.75)
    assert mt.get_gauge("cpu") == 0.75


def test_avg():
    mt = MetricTracker()
    for v in [1.0, 2.0, 3.0]:
        mt.record("latency", v)
    assert mt.avg("latency") == 2.0


def test_p95():
    mt = MetricTracker()
    for v in range(1, 101):
        mt.record("latency", float(v))
    assert mt.p95("latency") >= 95.0


def test_reset():
    mt = MetricTracker()
    mt.increment("x"); mt.gauge("y", 1)
    mt.reset()
    assert mt.counter("x") == 0 and mt.get_gauge("y") is None
