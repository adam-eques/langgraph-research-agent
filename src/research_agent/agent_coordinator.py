from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AgentStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    payload: Any
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "has_result": self.result is not None,
            "error": self.error,
        }


AgentFn = Callable[[Any], Any]
AsyncAgentFn = Callable[[Any], Coroutine[Any, Any, None]]


class AgentCoordinator:
    def __init__(self, max_concurrency: int = 4) -> None:
        self._agents: dict[str, AgentFn | AsyncAgentFn] = {}
        self._tasks: list[AgentTask] = []
        self._max_concurrency = max_concurrency
        self._task_counter = 0

    def register(self, name: str, fn: AgentFn | AsyncAgentFn) -> None:
        self._agents[name] = fn

    def unregister(self, name: str) -> bool:
        return self._agents.pop(name, None) is not None

    def _next_id(self) -> str:
        self._task_counter += 1
        return f"task-{self._task_counter:04d}"

    def submit(self, agent_name: str, payload: Any) -> AgentTask:
        task = AgentTask(
            task_id=self._next_id(),
            agent_name=agent_name,
            payload=payload,
        )
        self._tasks.append(task)
        return task

    def run_sync(self, task: AgentTask) -> AgentTask:
        fn = self._agents.get(task.agent_name)
        if fn is None:
            task.status = AgentStatus.FAILED
            task.error = f"Agent '{task.agent_name}' not registered."
            return task
        task.status = AgentStatus.RUNNING
        try:
            task.result = fn(task.payload)
            task.status = AgentStatus.DONE
        except Exception as exc:
            task.status = AgentStatus.FAILED
            task.error = str(exc)
        return task

    async def run_async(self, task: AgentTask) -> AgentTask:
        fn = self._agents.get(task.agent_name)
        if fn is None:
            task.status = AgentStatus.FAILED
            task.error = f"Agent '{task.agent_name}' not registered."
            return task
        task.status = AgentStatus.RUNNING
        try:
            result = fn(task.payload)
            if asyncio.iscoroutine(result):
                task.result = await result
            else:
                task.result = result
            task.status = AgentStatus.DONE
        except Exception as exc:
            task.status = AgentStatus.FAILED
            task.error = str(exc)
        return task

    async def run_all_async(self, tasks: list[AgentTask]) -> list[AgentTask]:
        sem = asyncio.Semaphore(self._max_concurrency)

        async def _run(t: AgentTask) -> AgentTask:
            async with sem:
                return await self.run_async(t)

        return list(await asyncio.gather(*[_run(t) for t in tasks]))

    def summary(self) -> dict:
        total = len(self._tasks)
        done = sum(1 for t in self._tasks if t.status == AgentStatus.DONE)
        failed = sum(1 for t in self._tasks if t.status == AgentStatus.FAILED)
        return {"total": total, "done": done, "failed": failed, "agents": list(self._agents)}
