from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ScheduleType(StrEnum):
    ONCE = "once"
    INTERVAL = "interval"
    CRON_LIKE = "cron_like"


@dataclass
class ScheduledJob:
    name: str
    fn: Callable[..., Awaitable[Any]]
    schedule_type: ScheduleType
    interval_seconds: float = 60.0
    max_runs: int = -1
    run_count: int = field(default=0, init=False)
    last_run: float = field(default=0.0, init=False)
    enabled: bool = True

    def is_due(self) -> bool:
        if not self.enabled:
            return False
        if self.max_runs > 0 and self.run_count >= self.max_runs:
            return False
        if self.schedule_type == ScheduleType.ONCE:
            return self.run_count == 0
        return time.monotonic() - self.last_run >= self.interval_seconds


class PipelineScheduler:
    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False

    def register(
        self,
        name: str,
        fn: Callable[..., Awaitable[Any]],
        schedule_type: ScheduleType = ScheduleType.INTERVAL,
        interval_seconds: float = 60.0,
        max_runs: int = -1,
    ) -> None:
        self._jobs[name] = ScheduledJob(
            name=name,
            fn=fn,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            max_runs=max_runs,
        )

    def unregister(self, name: str) -> bool:
        return self._jobs.pop(name, None) is not None

    async def tick(self) -> list[str]:
        ran = []
        for job in list(self._jobs.values()):
            if job.is_due():
                try:
                    await job.fn()
                    job.run_count += 1
                    job.last_run = time.monotonic()
                    ran.append(job.name)
                except Exception:
                    pass
        return ran

    def job_names(self) -> list[str]:
        return list(self._jobs.keys())
