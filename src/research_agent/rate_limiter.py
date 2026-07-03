from __future__ import annotations

import asyncio
import time


class TokenBucketLimiter:
    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last_refill = now

    async def acquire(self, tokens: float = 1.0) -> None:
        async with self._lock:
            self._refill()
            while self._tokens < tokens:
                wait = (tokens - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._refill()
            self._tokens -= tokens

    def available(self) -> float:
        self._refill()
        return self._tokens


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._calls: list[float] = []

    def allow(self) -> bool:
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < self._window]
        if len(self._calls) < self._max:
            self._calls.append(now)
            return True
        return False

    def reset(self) -> None:
        self._calls.clear()


class RateLimiter:
    """Per-client sliding-window rate limiter.

    Tracks request timestamps independently for each client key and allows up
    to ``max_requests`` within any ``window_seconds`` interval.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._clients: dict[str, list[float]] = {}

    def _active(self, client_id: str) -> list[float]:
        now = time.monotonic()
        calls = [t for t in self._clients.get(client_id, []) if now - t < self._window]
        self._clients[client_id] = calls
        return calls

    def is_allowed(self, client_id: str) -> bool:
        calls = self._active(client_id)
        if len(calls) < self._max:
            calls.append(time.monotonic())
            return True
        return False

    def remaining(self, client_id: str) -> int:
        return self._max - len(self._active(client_id))

    def reset(self, client_id: str) -> None:
        self._clients.pop(client_id, None)
