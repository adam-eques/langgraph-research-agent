from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None


class TaskTracker:
    """Track sub-task states within a multi-step research session."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task_id: str, description: str) -> Task:
        task = Task(id=task_id, description=description)
        self._tasks[task_id] = task
        logger.debug("Task added: %s — %s", task_id, description)
        return task

    def start(self, task_id: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].status = TaskStatus.IN_PROGRESS

    def complete(self, task_id: str, result: Any = None) -> None:
        if task_id in self._tasks:
            t = self._tasks[task_id]
            t.status = TaskStatus.COMPLETE
            t.result = result

    def fail(self, task_id: str, error: str) -> None:
        if task_id in self._tasks:
            t = self._tasks[task_id]
            t.status = TaskStatus.FAILED
            t.error = error

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for t in self._tasks.values():
            counts[t.status] = counts.get(t.status, 0) + 1
        return counts
