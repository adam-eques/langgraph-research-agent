from __future__ import annotations

import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Register and look up available agent node builders by name."""

    def __init__(self) -> None:
        self._registry: dict[str, Callable] = {}

    def register(self, name: str, builder: Callable, overwrite: bool = False) -> None:
        if name in self._registry and not overwrite:
            raise ValueError(
                f"Agent '{name}' is already registered. Use overwrite=True to replace."
            )
        self._registry[name] = builder
        logger.debug("Registered agent: %s", name)

    def get(self, name: str) -> Callable | None:
        builder = self._registry.get(name)
        if builder is None:
            logger.warning("Agent not found in registry: %s", name)
        return builder

    def list_agents(self) -> list[str]:
        return sorted(self._registry.keys())

    def is_registered(self, name: str) -> bool:
        return name in self._registry
