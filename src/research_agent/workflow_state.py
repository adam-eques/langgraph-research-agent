from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class WorkflowStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowState:
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.IDLE
    current_step: str = ""
    steps_completed: list[str] = field(default_factory=list)
    steps_failed: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    started_at: float = 0.0
    completed_at: float = 0.0

    def start(self) -> None:
        self.status = WorkflowStatus.RUNNING
        self.started_at = time.monotonic()

    def complete_step(self, step: str) -> None:
        self.steps_completed.append(step)
        self.current_step = step

    def fail_step(self, step: str, error: str = "") -> None:
        self.steps_failed.append(step)
        self.error = error
        self.status = WorkflowStatus.FAILED

    def finish(self) -> None:
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = time.monotonic()

    @property
    def elapsed(self) -> float:
        if self.started_at == 0:
            return 0.0
        end = self.completed_at if self.completed_at else time.monotonic()
        return end - self.started_at

    def is_done(self) -> bool:
        return self.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)
