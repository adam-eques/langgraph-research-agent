from __future__ import annotations

from langchain_community.tools.tavily_search import TavilySearchResults

from research_agent.config import config


def get_search_tool() -> TavilySearchResults:
    # Pass a placeholder key when none is configured so the tool (and the graph
    # that builds it) can be constructed without credentials; real searches at
    # runtime still require a valid TAVILY_API_KEY.
    return TavilySearchResults(
        max_results=config.max_search_results,
        include_answer=True,
        include_raw_content=False,
        tavily_api_key=config.tavily_api_key or "tvly-placeholder",
    )
