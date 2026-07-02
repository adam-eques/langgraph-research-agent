from __future__ import annotations

import logging
from typing import Any, cast

logger = logging.getLogger(__name__)


def count_tokens_anthropic(
    messages: list[dict[str, Any]], model: str = "claude-3-5-sonnet-20241022"
) -> int:
    """Count tokens using the Anthropic messages API.

    Requires ANTHROPIC_API_KEY and anthropic SDK.
    Returns -1 if counting fails (non-fatal).
    """
    try:
        import anthropic

        from research_agent.config import config

        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        result = client.messages.count_tokens(
            model=model,
            messages=cast(Any, messages),
        )
        logger.debug("Token count for %d messages: %d", len(messages), result.input_tokens)
        return result.input_tokens
    except Exception as exc:
        logger.debug("Token counting failed: %s", exc)
        return -1


def estimate_tokens_simple(text: str) -> int:
    """Fast token estimate without an API call: chars / 4."""
    return max(1, len(text) // 4)


def warn_if_over_budget(tokens: int, budget: int, label: str = "request") -> None:
    """Log a warning if tokens exceed budget."""
    if tokens > budget:
        logger.warning(
            "%s uses %d tokens (budget: %d, overage: %d)",
            label,
            tokens,
            budget,
            tokens - budget,
        )
    else:
        logger.debug("%s uses %d/%d tokens (%.0f%%)", label, tokens, budget, 100 * tokens / budget)


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
