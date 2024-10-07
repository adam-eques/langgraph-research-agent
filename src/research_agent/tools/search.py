from __future__ import annotations

from langchain_community.tools.tavily_search import TavilySearchResults
from research_agent.config import config


def get_search_tool() -> TavilySearchResults:
    return TavilySearchResults(
        max_results=config.max_search_results,
        include_answer=True,
        include_raw_content=False,
    )
