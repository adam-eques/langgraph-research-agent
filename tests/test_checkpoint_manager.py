from __future__ import annotations

from research_agent.checkpoint_manager import CheckpointManager


def test_save_and_load(tmp_path):
    mgr = CheckpointManager(str(tmp_path / "cp"))
    mgr.save("run1", {"query": "AI"}, step=1)
    cp = mgr.load_latest("run1")
    assert cp["run_id"] == "run1" and cp["state"]["query"] == "AI"


def test_load_missing(tmp_path):
    mgr = CheckpointManager(str(tmp_path / "cp"))
    assert mgr.load_latest("nonexistent") is None


def test_list_runs(tmp_path):
    mgr = CheckpointManager(str(tmp_path / "cp"))
    mgr.save("runA", {}, step=1)
    mgr.save("runB", {}, step=1)
    assert "runA" in mgr.list_runs() and "runB" in mgr.list_runs()


def test_delete(tmp_path):
    mgr = CheckpointManager(str(tmp_path / "cp"))
    mgr.save("run1", {}, step=1)
    mgr.save("run1", {}, step=2)
    assert mgr.delete("run1") == 2
