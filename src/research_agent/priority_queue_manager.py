from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityItem:
    priority: int
    sequence: int
    payload: Any = field(compare=False)
    tags: list[str] = field(default_factory=list, compare=False)

    def to_dict(self) -> dict:
        return {
            "priority": self.priority,
            "sequence": self.sequence,
            "tags": self.tags,
        }


class PriorityQueueManager:
    def __init__(self) -> None:
        self._heap: list[PriorityItem] = []
        self._seq = 0
        self._total_enqueued = 0
        self._total_dequeued = 0

    def enqueue(
        self,
        payload: Any,
        priority: int = 5,
        tags: list[str] | None = None,
    ) -> PriorityItem:
        item = PriorityItem(
            priority=priority,
            sequence=self._seq,
            payload=payload,
            tags=tags or [],
        )
        heapq.heappush(self._heap, item)
        self._seq += 1
        self._total_enqueued += 1
        return item

    def dequeue(self) -> PriorityItem | None:
        if not self._heap:
            return None
        item = heapq.heappop(self._heap)
        self._total_dequeued += 1
        return item

    def peek(self) -> PriorityItem | None:
        return self._heap[0] if self._heap else None

    def drain(self) -> list[PriorityItem]:
        items: list[PriorityItem] = []
        while self._heap:
            items.append(heapq.heappop(self._heap))
        self._total_dequeued += len(items)
        return items

    def filter_by_tag(self, tag: str) -> list[PriorityItem]:
        return [item for item in self._heap if tag in item.tags]

    @property
    def size(self) -> int:
        return len(self._heap)

    @property
    def stats(self) -> dict:
        return {
            "size": self.size,
            "total_enqueued": self._total_enqueued,
            "total_dequeued": self._total_dequeued,
        }
