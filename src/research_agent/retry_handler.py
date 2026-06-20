from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = False
    retryable_exceptions: tuple = (Exception,)


@dataclass
class RetryResult:
    value: Any
    attempts: int
    succeeded: bool
    errors: list[str] = field(default_factory=list)


def compute_delay(attempt: int, config: RetryConfig) -> float:
    delay = config.base_delay * (config.backoff_factor ** (attempt - 1))
    return min(delay, config.max_delay)


def retry_sync(
    fn: Callable[[], Any],
    config: RetryConfig | None = None,
) -> RetryResult:
    cfg = config or RetryConfig()
    errors: list[str] = []
    for attempt in range(1, cfg.max_attempts + 1):
        try:
            value = fn()
            return RetryResult(value=value, attempts=attempt, succeeded=True, errors=errors)
        except cfg.retryable_exceptions as exc:
            errors.append(str(exc))
            if attempt < cfg.max_attempts:
                time.sleep(compute_delay(attempt, cfg))
    return RetryResult(value=None, attempts=cfg.max_attempts, succeeded=False, errors=errors)


async def retry_async(
    fn: Callable[[], Awaitable[Any]],
    config: RetryConfig | None = None,
) -> RetryResult:
    cfg = config or RetryConfig()
    errors: list[str] = []
    for attempt in range(1, cfg.max_attempts + 1):
        try:
            value = await fn()
            return RetryResult(value=value, attempts=attempt, succeeded=True, errors=errors)
        except cfg.retryable_exceptions as exc:
            errors.append(str(exc))
            if attempt < cfg.max_attempts:
                await asyncio.sleep(compute_delay(attempt, cfg))
    return RetryResult(value=None, attempts=cfg.max_attempts, succeeded=False, errors=errors)


class RetryHandler:
    def __init__(self, config: RetryConfig | None = None) -> None:
        self._config = config or RetryConfig()

    def run(self, fn: Callable[[], Any]) -> RetryResult:
        return retry_sync(fn, self._config)

    async def run_async(self, fn: Callable[[], Awaitable[Any]]) -> RetryResult:
        return await retry_async(fn, self._config)

    def with_config(self, **kwargs) -> "RetryHandler":
        import dataclasses
        cfg = dataclasses.replace(self._config, **kwargs)
        return RetryHandler(cfg)
