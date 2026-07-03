from __future__ import annotations

import time

from research_agent.pipeline_monitor import PipelineMonitor


def test_node_started_and_finished():
    pm = PipelineMonitor("pipe-1")
    run = pm.node_started("retrieve")
    time.sleep(0.005)
    pm.node_finished(run, output={"docs": [1, 2]})
    assert run.status == "success" and run.duration_ms >= 5


def test_node_failed():
    pm = PipelineMonitor("pipe-2")
    run = pm.node_started("analyse")
    pm.node_failed(run, "timeout")
    assert run.status == "error" and run.error == "timeout"


def test_summary_counts():
    pm = PipelineMonitor("pipe-3")
    r1 = pm.node_started("step1")
    pm.node_finished(r1)
    r2 = pm.node_started("step2")
    pm.node_failed(r2, "err")
    s = pm.summary()
    assert s["nodes_succeeded"] == 1 and s["nodes_failed"] == 1


def test_total_duration_positive():
    pm = PipelineMonitor("pipe-4")
    assert pm.total_duration_ms >= 0
