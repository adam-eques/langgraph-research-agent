from __future__ import annotations
import logging
from typing import Any
logger = logging.getLogger(__name__)

_SYNTHESIS_SYSTEM = """You are an expert research synthesizer.
Given multiple research notes, synthesize a comprehensive, well-structured answer.
Cite sources where relevant. Be accurate, concise, and avoid repetition."""

async def synthesize_answer(
    query: str,
    notes: list[str],
    citations: list[dict],
    llm,
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    from research_agent.context_builder import summarize_notes, format_citations
    notes_text = summarize_notes(notes, max_chars=5000)
    citations_text = format_citations(citations)
    content = f"Query: {query}\n\nResearch Notes:\n{notes_text}"
    if citations_text:
        content += f"\n\n{citations_text}"
    msgs = [SystemMessage(content=_SYNTHESIS_SYSTEM), HumanMessage(content=content)]
    response = await llm.ainvoke(msgs)
    answer = response.content if hasattr(response, "content") else str(response)
    logger.debug("Synthesized answer: %d chars", len(answer))
    return answer.strip()
