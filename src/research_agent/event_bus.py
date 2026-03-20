from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """Simple async publish-subscribe bus for agent coordination events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)
        logger.debug("Subscribed to event: %s", event)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event] = [h for h in self._handlers[event] if h is not handler]

    async def publish(self, event: str, data: Any = None) -> None:
        handlers = list(self._handlers.get(event, []))
        logger.debug("Publishing event %s to %d handlers", event, len(handlers))
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                handler(data)

    @property
    def subscribed_events(self) -> list[str]:
        return list(self._handlers.keys())
