from __future__ import annotations

import time

from research_agent.rate_limiter import RateLimiter


def test_allows_within_limit():
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        assert limiter.is_allowed("client1") is True


def test_blocks_over_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        limiter.is_allowed("client1")
    assert limiter.is_allowed("client1") is False


def test_different_clients_independent():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    for _ in range(2):
        limiter.is_allowed("client1")
    assert limiter.is_allowed("client1") is False
    assert limiter.is_allowed("client2") is True  # separate bucket


def test_remaining_decrements():
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    assert limiter.remaining("new_client") == 5
    limiter.is_allowed("new_client")
    assert limiter.remaining("new_client") == 4


def test_reset_clears_client():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("c")
    limiter.is_allowed("c")
    limiter.reset("c")
    assert limiter.remaining("c") == 2


def test_rate_limiter_window_expiry():
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    limiter.is_allowed("c")
    limiter.is_allowed("c")
    assert limiter.is_allowed("c") is False
    time.sleep(1.1)
    assert limiter.is_allowed("c") is True
