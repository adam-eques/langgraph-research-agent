from __future__ import annotations

import logging
from typing import cast

logger = logging.getLogger(__name__)

_PLANNER_SYSTEM = """You are a research query planner.
Given a complex research question, break it into 3-5 focused sub-questions
that can be researched independently. Return JSON: {"sub_queries": ["...", "..."]}.
Each sub-query should be self-contained and researchable via web search."""


async def plan_query(query: str, llm) -> list[str]:
    from langchain_core.messages import HumanMessage, SystemMessage

    from research_agent.output_validator import extract_and_parse_json

    msgs = [
        SystemMessage(content=_PLANNER_SYSTEM),
        HumanMessage(content=f"Break down this query: {query}"),
    ]
    response = await llm.ainvoke(msgs)
    content = response.content if hasattr(response, "content") else str(response)
    parsed = extract_and_parse_json(content)
    if parsed and "sub_queries" in parsed:
        return cast(list[str], parsed["sub_queries"])
    logger.warning("Planner returned unparseable output, using original query")
    return [query]
