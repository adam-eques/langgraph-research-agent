from __future__ import annotations

from research_agent.task_tracker import TaskStatus, TaskTracker


def test_add_and_start():
    tt = TaskTracker()
    tt.add("t1", "Search for papers")
    tt.start("t1")
    assert tt._tasks["t1"].status == TaskStatus.IN_PROGRESS


def test_complete():
    tt = TaskTracker()
    tt.add("t1", "Research")
    tt.complete("t1", result={"answer": "42"})
    assert tt._tasks["t1"].status == TaskStatus.COMPLETE
    assert tt._tasks["t1"].result == {"answer": "42"}


def test_fail():
    tt = TaskTracker()
    tt.add("t1", "Research")
    tt.fail("t1", error="LLM timeout")
    assert tt._tasks["t1"].status == TaskStatus.FAILED
    assert "timeout" in tt._tasks["t1"].error


def test_summary():
    tt = TaskTracker()
    tt.add("t1", "A")
    tt.add("t2", "B")
    tt.complete("t1")
    s = tt.summary()
    assert s[TaskStatus.COMPLETE] == 1
    assert s[TaskStatus.PENDING] == 1
