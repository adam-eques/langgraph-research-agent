from __future__ import annotations

import asyncio
import pytest
from research_agent.event_bus import EventBus


@pytest.mark.asyncio
async def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    def handler(data):
        received.append(data)
    bus.subscribe("research_done", handler)
    await bus.publish("research_done", {"answer": "42"})
    assert received == [{"answer": "42"}]


@pytest.mark.asyncio
async def test_async_handler():
    bus = EventBus()
    received = []
    async def handler(data):
        received.append(data)
    bus.subscribe("done", handler)
    await bus.publish("done", "ok")
    assert received == ["ok"]


@pytest.mark.asyncio
async def test_unsubscribe():
    bus = EventBus()
    received = []
    def handler(data):
        received.append(data)
    bus.subscribe("e", handler)
    bus.unsubscribe("e", handler)
    await bus.publish("e", "data")
    assert received == []
