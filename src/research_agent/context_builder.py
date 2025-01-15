from __future__ import annotations

import logging
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)

_TOKEN_ESTIMATE = 4  # chars per token (rough estimate)


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars / 4."""
    return max(1, len(text) // _TOKEN_ESTIMATE)


def build_context_window(
    messages: list[BaseMessage],
    max_tokens: int = 8000,
    system_budget: int = 1000,
) -> list[BaseMessage]:
    """Trim message history to fit within a token budget.

    Keeps the system message intact, then fills from the most recent
    messages backwards until the budget is exhausted.
    """
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]

    system_tokens = sum(estimate_tokens(str(m.content)) for m in system_msgs)
    remaining = max_tokens - system_tokens - system_budget
    if remaining <= 0:
        logger.warning("System messages alone exceed context budget")
        return system_msgs

    selected: list[BaseMessage] = []
    token_count = 0
    for msg in reversed(other_msgs):
        msg_tokens = estimate_tokens(str(msg.content))
        if token_count + msg_tokens > remaining:
            break
        selected.insert(0, msg)
        token_count += msg_tokens

    logger.debug(
        "Context window: %d/%d messages kept (%d estimated tokens)",
        len(selected),
        len(other_msgs),
        token_count,
    )
    return system_msgs + selected


def summarize_notes(notes: list[str], max_chars: int = 4000) -> str:
    """Concatenate research notes, truncating to max_chars."""
    full = "\n\n".join(notes)
    if len(full) <= max_chars:
        return full
    logger.debug("Truncating research notes from %d to %d chars", len(full), max_chars)
    return full[:max_chars] + "\n\n[...truncated]"
