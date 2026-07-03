from __future__ import annotations

import pytest

from research_agent.error_recovery import safe_dict_get, with_default_on_error, with_fallback


@pytest.mark.asyncio
async def test_with_fallback_uses_primary():
    async def primary():
        return "primary"

    async def fallback():
        return "fallback"

    result = await with_fallback(primary, fallback)
    assert result == "primary"


@pytest.mark.asyncio
async def test_with_fallback_falls_back():
    async def primary():
        raise RuntimeError("fail")

    async def fallback():
        return "fallback"

    result = await with_fallback(primary, fallback)
    assert result == "fallback"


@pytest.mark.asyncio
async def test_with_default_on_error():
    async def failing():
        raise ValueError("oops")

    result = await with_default_on_error(failing, "default")
    assert result == "default"


def test_safe_dict_get():
    data = {"a": {"b": {"c": 42}}}
    assert safe_dict_get(data, "a", "b", "c") == 42
    assert safe_dict_get(data, "a", "x", default="missing") == "missing"
