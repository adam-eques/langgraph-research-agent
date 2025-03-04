

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
