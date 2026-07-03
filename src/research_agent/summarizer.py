from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_SUMMARIZER_SYSTEM = (
    "You are a concise summarizer. Given research notes, produce a "
    "3-5 sentence summary covering the key findings. Be factual and direct."
)


async def summarize_with_llm(notes: str, llm) -> str:
    """Use an LLM to produce a concise summary of research notes."""
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=_SUMMARIZER_SYSTEM),
        HumanMessage(content=f"Summarize these research notes:\n\n{notes[:6000]}"),
    ]
    result = await llm.ainvoke(messages)
    text = result.content if hasattr(result, "content") else str(result)
    logger.debug("Summary generated: %d chars", len(text))
    return text.strip()


def extractive_summary(text: str, n_sentences: int = 3) -> str:
    """Simple extractive summary: return first N sentences."""
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:n_sentences])
