

def log_token_usage(prompt_tokens: int, completion_tokens: int, model: str = "") -> None:
    """Log token usage in a consistent format for cost tracking."""
    total = prompt_tokens + completion_tokens
    logger.info(
        "Token usage | model=%s prompt=%d completion=%d total=%d",
        model or "unknown",
        prompt_tokens,
        completion_tokens,
        total,
    )
