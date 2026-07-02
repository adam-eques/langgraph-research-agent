from __future__ import annotations
from research_agent.workflow_checkpoint import WorkflowCheckpoint, WorkflowCheckpointer


def test_save_and_load(tmp_path):
    cp = WorkflowCheckpoint("cp1", "wf1", "step_A", {"k": "v"})
    checkpointer = WorkflowCheckpointer(str(tmp_path))
    checkpointer.save(cp)
    loaded = checkpointer.load("cp1")
    assert loaded is not None and loaded.step == "step_A"


def test_load_missing(tmp_path):
    checkpointer = WorkflowCheckpointer(str(tmp_path))
    assert checkpointer.load("nonexistent") is None


def test_delete(tmp_path):
    cp = WorkflowCheckpoint("cp2", "wf1", "step_B", {})
    checkpointer = WorkflowCheckpointer(str(tmp_path))
    checkpointer.save(cp)
    assert checkpointer.delete("cp2") is True
    assert checkpointer.load("cp2") is None


def test_list_for_workflow(tmp_path):
    checkpointer = WorkflowCheckpointer(str(tmp_path))
    checkpointer.save(WorkflowCheckpoint("a1", "wf_x", "s1", {}))
    checkpointer.save(WorkflowCheckpoint("a2", "wf_x", "s2", {}))
    checkpointer.save(WorkflowCheckpoint("a3", "wf_y", "s1", {}))
    cps = checkpointer.list_for_workflow("wf_x")
    assert len(cps) == 2


def test_latest(tmp_path):
    checkpointer = WorkflowCheckpointer(str(tmp_path))
    checkpointer.save(WorkflowCheckpoint("b1", "wf_z", "s1", {}, created_at=1000.0))
    checkpointer.save(WorkflowCheckpoint("b2", "wf_z", "s2", {}, created_at=2000.0))
    latest = checkpointer.latest("wf_z")
    assert latest.checkpoint_id == "b2"


def test_to_dict_and_from_dict():
    cp = WorkflowCheckpoint("c1", "wf1", "step", {"x": 1})
    d = cp.to_dict()
    restored = WorkflowCheckpoint.from_dict(d)
    assert restored.checkpoint_id == "c1" and restored.state == {"x": 1}
