from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        fn: Callable,
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        if name in self._nodes:
            logger.warning("Node %r already registered; overwriting", name)
        self._nodes[name] = {"fn": fn, "description": description, "tags": tags or []}
        logger.debug("Registered node: %s", name)

    def get(self, name: str) -> Callable | None:
        entry = self._nodes.get(name)
        return entry["fn"] if entry else None

    def list_names(self) -> list[str]:
        return sorted(self._nodes.keys())

    def by_tag(self, tag: str) -> list[str]:
        return [n for n, meta in self._nodes.items() if tag in meta.get("tags", [])]

    def describe(self, name: str) -> str:
        entry = self._nodes.get(name)
        return entry["description"] if entry else ""

    def unregister(self, name: str) -> bool:
        return self._nodes.pop(name, None) is not None

    def __len__(self) -> int:
        return len(self._nodes)
