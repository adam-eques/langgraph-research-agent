from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TruncationStrategy(StrEnum):
    TAIL = "tail"
    HEAD = "head"
    MIDDLE = "middle"
    SENTENCE_BOUNDARY = "sentence_boundary"


@dataclass
class TruncationPolicy:
    max_chars: int
    strategy: TruncationStrategy = TruncationStrategy.TAIL
    ellipsis: str = "..."
    preserve_sentences: bool = True


def truncate(text: str, policy: TruncationPolicy) -> str:
    if len(text) <= policy.max_chars:
        return text
    limit = policy.max_chars - len(policy.ellipsis)
    if limit <= 0:
        return policy.ellipsis

    if policy.strategy == TruncationStrategy.HEAD:
        return policy.ellipsis + text[-limit:]

    if policy.strategy == TruncationStrategy.MIDDLE:
        half = limit // 2
        return text[:half] + policy.ellipsis + text[-(limit - half) :]

    if policy.strategy == TruncationStrategy.SENTENCE_BOUNDARY:
        truncated = text[:limit]
        last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
        if last_period > limit // 2:
            return truncated[: last_period + 1] + policy.ellipsis
        return truncated + policy.ellipsis

    return text[:limit] + policy.ellipsis


def truncate_list(items: list[str], max_items: int, policy: TruncationPolicy) -> list[str]:
    truncated = items[:max_items]
    return [truncate(item, policy) for item in truncated]
