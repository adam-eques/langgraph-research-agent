from __future__ import annotations

import pytest

from research_agent.agent_coordinator import AgentCoordinator, AgentStatus


def test_register_and_run_sync():
    coord = AgentCoordinator()
    coord.register("upper", lambda x: x.upper())
    task = coord.submit("upper", "hello")
    coord.run_sync(task)
    assert task.status == AgentStatus.DONE and task.result == "HELLO"


def test_run_sync_unknown_agent():
    coord = AgentCoordinator()
    task = coord.submit("missing", "data")
    coord.run_sync(task)
    assert task.status == AgentStatus.FAILED and "not registered" in task.error


def test_run_sync_exception_captured():
    coord = AgentCoordinator()
    coord.register("exploder", lambda x: (_ for _ in ()).throw(ValueError("boom")))
    task = coord.submit("exploder", None)
    coord.run_sync(task)
    assert task.status == AgentStatus.FAILED and "boom" in task.error


def test_unregister():
    coord = AgentCoordinator()
    coord.register("fn", lambda x: x)
    removed = coord.unregister("fn")
    assert removed is True
    assert coord.unregister("fn") is False


def test_summary():
    coord = AgentCoordinator()
    coord.register("fn", lambda x: x)
    t1 = coord.submit("fn", "a")
    t2 = coord.submit("fn", "b")
    coord.run_sync(t1)
    coord.run_sync(t2)
    s = coord.summary()
    assert s["done"] == 2 and s["total"] == 2


@pytest.mark.asyncio
async def test_run_async():
    coord = AgentCoordinator()
    coord.register("double", lambda x: x * 2)
    task = coord.submit("double", 5)
    await coord.run_async(task)
    assert task.result == 10 and task.status == AgentStatus.DONE
