from __future__ import annotations

from research_agent.agent_trace import AgentTrace


def test_record_and_summary():
    trace = AgentTrace()
    trace.record("retriever", {"query": "q"}, {"docs": []}, 12.5)
    s = trace.summary()
    assert s["total_steps"] == 1
    assert s["total_ms"] == 12.5
    assert "retriever" in s["nodes"]


def test_empty_summary():
    trace = AgentTrace()
    assert trace.summary()["total_steps"] == 0


def test_to_json():
    trace = AgentTrace()
    trace.record("researcher", {}, {}, 20.0)
    j = trace.to_json()
    assert "researcher" in j
    assert "total_steps" in j


def test_save_creates_file(tmp_path):
    trace = AgentTrace()
    trace.record("analyst", {}, {}, 5.0)
    out = str(tmp_path / "trace.json")
    trace.save(out)
    import json

    data = json.loads((tmp_path / "trace.json").read_text())
    assert data["summary"]["total_steps"] == 1
