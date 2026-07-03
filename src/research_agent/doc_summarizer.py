from __future__ import annotations

import re


def extractive_summary(text: str, num_sentences: int = 3) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    if not sentences:
        return text[:500]
    step = max(1, len(sentences) // num_sentences)
    selected = sentences[:1]
    for i in range(step, len(sentences), step):
        if len(selected) < num_sentences:
            selected.append(sentences[i])
    if len(sentences) > 1 and sentences[-1] not in selected and len(selected) < num_sentences:
        selected.append(sentences[-1])
    return " ".join(selected)


def truncate_summary(text: str, max_chars: int = 500) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_end = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
    if last_end > max_chars // 2:
        return truncated[: last_end + 1]
    return truncated + "..."


def summarize_batch(documents: list[str], num_sentences: int = 2) -> list[str]:
    return [extractive_summary(doc, num_sentences) for doc in documents]


def merge_summaries(summaries: list[str], separator: str = "\n\n") -> str:
    seen: set[str] = set()
    unique = []
    for s in summaries:
        normalized = s.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s.strip())
    return separator.join(unique)
