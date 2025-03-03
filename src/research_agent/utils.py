

def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Async version of the retry decorator with exponential backoff."""
    import asyncio
    import functools

    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            raise RuntimeError(f"All {max_attempts} attempts failed") from last_exc
        return wrapper
    return decorator
