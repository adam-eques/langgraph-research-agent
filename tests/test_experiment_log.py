from __future__ import annotations

from research_agent.experiment_log import ExperimentLog


def test_log_and_load(tmp_path):
    log = ExperimentLog(str(tmp_path / "exp.jsonl"))
    log.log("exp1", "claude-3-5-sonnet", {"temp": 0.0}, {"score": 0.9})
    entries = log.load_all()
    assert len(entries) == 1
    assert entries[0]["experiment_id"] == "exp1"


def test_filter_by_model(tmp_path):
    log = ExperimentLog(str(tmp_path / "exp.jsonl"))
    log.log("e1", "claude", {}, {"score": 0.9})
    log.log("e2", "gpt-4", {}, {"score": 0.8})
    claude_runs = log.filter_by_model("claude")
    assert len(claude_runs) == 1
    assert claude_runs[0]["experiment_id"] == "e1"


def test_empty_log(tmp_path):
    log = ExperimentLog(str(tmp_path / "nope.jsonl"))
    assert log.load_all() == []
