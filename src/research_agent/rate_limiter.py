"""Sliding-window rate limiter with FastAPI dependency integration."""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request, status

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory sliding-window rate limiter.

    Tracks request timestamps per ``client_id`` using a :class:`collections.deque`.
    Timestamps older than *window_seconds* are evicted on every check, so the
    deque only ever holds the requests that fall within the current window.

    This implementation is *not* thread-safe.  For production use with multiple
    workers, replace the in-memory store with a Redis-backed equivalent.

    Example
    -------
    >>> limiter = RateLimiter(max_requests=10, window_seconds=60)
    >>> limiter.is_allowed("user-123")
    True
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """
        Parameters
        ----------
        max_requests:
            Maximum number of requests allowed per *window_seconds*.
        window_seconds:
            Rolling window duration in seconds.
        """
        if max_requests <= 0:
            raise ValueError(f"max_requests must be positive; got {max_requests}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive; got {window_seconds}")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Stores request timestamps (float unix time) per client
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> bool:
        """Check whether *client_id* is within the rate limit.

        As a side-effect, records the current timestamp if the request is
        allowed.

        Parameters
        ----------
        client_id:
            Any string identifying the caller (IP, user ID, API key, etc.).

        Returns
        -------
        bool
            ``True`` if the request is within the allowed rate, ``False``
            otherwise.
        """
        now = time.monotonic()
        window = self._windows[client_id]
        cutoff = now - self.window_seconds

        # Evict stale timestamps from the left
        while window and window[0] < cutoff:
            window.popleft()

        if len(window) >= self.max_requests:
            logger.debug(
                "Rate limit exceeded for client %s (%d/%d requests in %ds window)",
                client_id,
                len(window),
                self.max_requests,
                self.window_seconds,
            )
            return False

        window.append(now)
        return True

    def reset(self, client_id: str) -> None:
        """Clear all recorded timestamps for *client_id*.

        Useful in tests or when a client's rate limit counter should be reset
        administratively.
        """
        self._windows.pop(client_id, None)

    def remaining(self, client_id: str) -> int:
        """Return the number of requests the client can still make in the current window.

        Does *not* record a request.
        """
        now = time.monotonic()
        window = self._windows[client_id]
        cutoff = now - self.window_seconds
        active = sum(1 for t in window if t >= cutoff)
        return max(0, self.max_requests - active)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

# Module-level default instance — replace with your own values or override
# the dependency to use per-route limits.
_default_limiter = RateLimiter(max_requests=60, window_seconds=60)


def check_rate_limit(
    request: Request,
    limiter: RateLimiter = Depends(lambda: _default_limiter),
) -> None:
    """FastAPI dependency that enforces the default rate limit.

    Uses the client's IP address as the ``client_id``.  Raises HTTP 429 when
    the limit is exceeded.

    Usage:

    .. code-block:: python

        @app.post("/research", dependencies=[Depends(check_rate_limit)])
        async def research(req: QueryRequest) -> QueryResponse: ...

    Or inject a custom limiter:

    .. code-block:: python

        from research_agent.rate_limiter import RateLimiter
        strict = RateLimiter(max_requests=10, window_seconds=60)

        @app.post("/expensive", dependencies=[Depends(lambda: check_rate_limit_with(strict))])
        async def expensive_route(): ...
    """
    client_ip = _get_client_ip(request)
    if not limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded: {limiter.max_requests} requests "
                f"per {limiter.window_seconds}s. Please slow down."
            ),
            headers={"Retry-After": str(limiter.window_seconds)},
        )


def check_rate_limit_with(limiter: RateLimiter):  # noqa: ANN201
    """Return a FastAPI dependency that uses *limiter* instead of the default."""

    def _dep(request: Request) -> None:
        client_ip = _get_client_ip(request)
        if not limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded: {limiter.max_requests} requests "
                    f"per {limiter.window_seconds}s."
                ),
                headers={"Retry-After": str(limiter.window_seconds)},
            )

    return _dep


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, honouring X-Forwarded-For when present."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
