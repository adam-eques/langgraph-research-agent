from __future__ import annotations
import pytest
from research_agent.event_emitter import EventEmitter, Event


def test_emit_calls_listener():
    emitter = EventEmitter()
    received = []
    emitter.on("data", lambda e: received.append(e.data))
    emitter.emit("data", data=42)
    assert received == [42]


def test_emit_no_listeners():
    emitter = EventEmitter()
    called = emitter.emit("noop")
    assert called == 0


def test_off_removes_listener():
    emitter = EventEmitter()
    fn = lambda e: None
    emitter.on("x", fn)
    removed = emitter.off("x", fn)
    assert removed is True and emitter.listener_count("x") == 0


def test_once_fires_only_once():
    emitter = EventEmitter()
    calls = []
    emitter.once("event", lambda e: calls.append(1))
    emitter.emit("event")
    emitter.emit("event")
    assert calls == [1]


def test_emit_count():
    emitter = EventEmitter()
    emitter.on("ping", lambda e: None)
    emitter.emit("ping")
    emitter.emit("ping")
    assert emitter.emit_count("ping") == 2


@pytest.mark.asyncio
async def test_emit_async():
    emitter = EventEmitter()
    received = []

    async def async_listener(e: Event):
        received.append(e.data)

    emitter.on_async("msg", async_listener)
    await emitter.emit_async("msg", data="hello")
    assert received == ["hello"]
