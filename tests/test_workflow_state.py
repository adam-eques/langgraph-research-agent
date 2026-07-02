from __future__ import annotations

from research_agent.workflow_state import WorkflowState, WorkflowStatus


def test_start_and_complete():
    ws = WorkflowState("wf-1")
    ws.start()
    ws.complete_step("retrieve")
    assert ws.status == WorkflowStatus.RUNNING
    assert "retrieve" in ws.steps_completed


def test_fail_step():
    ws = WorkflowState("wf-2")
    ws.start()
    ws.fail_step("analyse", "timeout error")
    assert ws.status == WorkflowStatus.FAILED
    assert ws.error == "timeout error"


def test_finish():
    ws = WorkflowState("wf-3")
    ws.start()
    ws.finish()
    assert ws.is_done() and ws.status == WorkflowStatus.COMPLETED


def test_elapsed_positive_after_start():
    import time

    ws = WorkflowState("wf-4")
    ws.start()
    time.sleep(0.01)
    assert ws.elapsed > 0
