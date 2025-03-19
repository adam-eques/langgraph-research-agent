

def test_async_retry_succeeds():
    import asyncio

    calls = []

    @async_retry(max_attempts=3, delay=0)
    async def fn():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("retry")
        return "ok"

    result = asyncio.run(fn())
    assert result == "ok"
    assert len(calls) == 2


def test_mask_api_key_short():
    from research_agent.utils import mask_api_key
    assert mask_api_key("abc") == "***"


def test_mask_api_key_long():
    from research_agent.utils import mask_api_key
    key = "sk-ant-api03-ABCDEF1234"
    masked = mask_api_key(key)
    assert masked.startswith("sk-ant-a")
    assert "..." in masked
