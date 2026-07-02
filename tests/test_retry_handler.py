from __future__ import annotations
import pytest
from research_agent.retry_handler import RetryConfig, RetryHandler, compute_delay, retry_sync


def test_retry_succeeds_first_try():
    handler = RetryHandler()
    result = handler.run(lambda: 42)
    assert result.succeeded and result.value == 42 and result.attempts == 1


def test_retry_succeeds_after_failures():
    call_count = [0]

    def flaky():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("fail")
        return "ok"

    cfg = RetryConfig(max_attempts=5, base_delay=0.0)
    handler = RetryHandler(cfg)
    result = handler.run(flaky)
    assert result.succeeded and result.value == "ok" and result.attempts == 3


def test_retry_exhausts_attempts():
    cfg = RetryConfig(max_attempts=2, base_delay=0.0)
    handler = RetryHandler(cfg)
    result = handler.run(lambda: (_ for _ in ()).throw(RuntimeError("always fails")))
    assert not result.succeeded and result.attempts == 2


def test_compute_delay_backoff():
    cfg = RetryConfig(base_delay=1.0, backoff_factor=2.0)
    assert compute_delay(1, cfg) == 1.0
    assert compute_delay(2, cfg) == 2.0
    assert compute_delay(3, cfg) == 4.0


def test_compute_delay_cap():
    cfg = RetryConfig(base_delay=1.0, backoff_factor=10.0, max_delay=5.0)
    assert compute_delay(5, cfg) == 5.0


@pytest.mark.asyncio
async def test_retry_async():
    cfg = RetryConfig(max_attempts=3, base_delay=0.0)
    handler = RetryHandler(cfg)

    async def async_ok():
        return "result"

    result = await handler.run_async(async_ok)
    assert result.succeeded and result.value == "result"
