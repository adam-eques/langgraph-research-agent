

def test_ingestion_error_path():
    from research_agent.exceptions import IngestionError
    exc = IngestionError("/docs/file.pdf", "permission denied")
    assert exc.path == "/docs/file.pdf"


def test_rate_limit_error():
    from research_agent.exceptions import RateLimitError
    exc = RateLimitError("user123", retry_after=30)
    assert exc.retry_after == 30
    assert "30s" in str(exc)
