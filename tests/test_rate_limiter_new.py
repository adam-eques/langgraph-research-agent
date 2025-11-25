from __future__ import annotations
from research_agent.rate_limiter import SlidingWindowLimiter


def test_allows_within_limit():
    lim = SlidingWindowLimiter(max_calls=3, window_seconds=60)
    assert lim.allow() and lim.allow() and lim.allow()


def test_blocks_over_limit():
    lim = SlidingWindowLimiter(max_calls=2, window_seconds=60)
    lim.allow(); lim.allow()
    assert lim.allow() is False


def test_reset_clears():
    lim = SlidingWindowLimiter(max_calls=1, window_seconds=60)
    lim.allow()
    assert lim.allow() is False
    lim.reset()
    assert lim.allow() is True
