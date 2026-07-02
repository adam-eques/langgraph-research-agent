from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable


class TaskPriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass(order=True)
class QueuedTask:
    priority: int
    created_at: float = field(compare=False, default_factory=time.monotonic)
    task_id: str = field(compare=False, default="")
    fn: Any = field(compare=False, default=None)
    args: tuple = field(compare=False, default_factory=tuple)
    kwargs: dict = field(compare=False, default_factory=dict)


class AsyncTaskQueue:
    def __init__(self, workers: int = 4) -> None:
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._workers = workers
        self._results: dict[str, Any] = {}
        self._errors: dict[str, Exception] = {}
        self._running = False

    async def submit(
        self,
        task_id: str,
        fn: Callable[..., Awaitable[Any]],
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs,
    ) -> None:
        task = QueuedTask(
            priority=-priority.value,
            task_id=task_id,
            fn=fn,
            args=args,
            kwargs=kwargs,
        )
        await self._queue.put(task)

    async def _worker(self) -> None:
        while True:
            task: QueuedTask = await self._queue.get()
            try:
                result = await task.fn(*task.args, **task.kwargs)
                self._results[task.task_id] = result
            except Exception as exc:
                self._errors[task.task_id] = exc
            finally:
                self._queue.task_done()

    async def run_until_empty(self) -> None:
        workers = [asyncio.create_task(self._worker()) for _ in range(self._workers)]
        await self._queue.join()
        for w in workers:
            w.cancel()

    def get_result(self, task_id: str) -> Any:
        return self._results.get(task_id)

    def get_error(self, task_id: str) -> Exception | None:
        return self._errors.get(task_id)
