

def test_rate_limiter_window_expiry():
    import time
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    limiter.is_allowed("c")
    limiter.is_allowed("c")
    assert limiter.is_allowed("c") is False
    time.sleep(1.1)
    assert limiter.is_allowed("c") is True
