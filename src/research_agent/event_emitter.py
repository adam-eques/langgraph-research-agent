from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    name: str
    data: Any = None
    source: str = ""
    metadata: dict = field(default_factory=dict)


ListenerFn = Callable[[Event], None]
AsyncListenerFn = Callable[[Event], "asyncio.Coroutine"]


class EventEmitter:
    def __init__(self) -> None:
        self._listeners: dict[str, list[ListenerFn]] = defaultdict(list)
        self._async_listeners: dict[str, list[AsyncListenerFn]] = defaultdict(list)
        self._emit_count: dict[str, int] = defaultdict(int)

    def on(self, event_name: str, fn: ListenerFn) -> None:
        self._listeners[event_name].append(fn)

    def on_async(self, event_name: str, fn: AsyncListenerFn) -> None:
        self._async_listeners[event_name].append(fn)

    def off(self, event_name: str, fn: ListenerFn) -> bool:
        listeners = self._listeners[event_name]
        try:
            listeners.remove(fn)
            return True
        except ValueError:
            return False

    def emit(self, event_name: str, data: Any = None, source: str = "") -> int:
        event = Event(name=event_name, data=data, source=source)
        self._emit_count[event_name] += 1
        called = 0
        for fn in list(self._listeners[event_name]):
            fn(event)
            called += 1
        return called

    async def emit_async(self, event_name: str, data: Any = None, source: str = "") -> int:
        event = Event(name=event_name, data=data, source=source)
        self._emit_count[event_name] += 1
        called = 0
        for fn in list(self._listeners[event_name]):
            fn(event)
            called += 1
        for fn in list(self._async_listeners[event_name]):
            await fn(event)
            called += 1
        return called

    def once(self, event_name: str, fn: ListenerFn) -> None:
        def wrapper(event: Event) -> None:
            fn(event)
            self.off(event_name, wrapper)

        self.on(event_name, wrapper)

    def listener_count(self, event_name: str) -> int:
        return len(self._listeners[event_name]) + len(self._async_listeners[event_name])

    def emit_count(self, event_name: str) -> int:
        return self._emit_count[event_name]

    def remove_all_listeners(self, event_name: str | None = None) -> None:
        if event_name:
            self._listeners[event_name].clear()
            self._async_listeners[event_name].clear()
        else:
            self._listeners.clear()
            self._async_listeners.clear()
