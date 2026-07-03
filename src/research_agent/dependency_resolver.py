from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Resolve execution order of tasks based on declared dependencies."""

    def __init__(self) -> None:
        self._tasks: dict[str, list[str]] = {}

    def register(self, task_id: str, depends_on: list[str] | None = None) -> None:
        self._tasks[task_id] = depends_on or []

    def resolve(self) -> list[str]:
        """Return tasks in topological order (Kahn algorithm)."""
        in_degree = {t: 0 for t in self._tasks}
        for t, deps in self._tasks.items():
            for _d in deps:
                in_degree[t] = in_degree.get(t, 0) + 1
        queue = [t for t, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for t, deps in self._tasks.items():
                if node in deps:
                    in_degree[t] -= 1
                    if in_degree[t] == 0:
                        queue.append(t)
        if len(order) != len(self._tasks):
            raise ValueError("Circular dependency detected")
        return order
