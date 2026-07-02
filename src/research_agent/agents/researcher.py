from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from research_agent.config import config
from research_agent.state import ResearchState
from research_agent.tools.search import get_search_tool

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a research specialist. Your job is to gather comprehensive, \
accurate information on the given topic using web search.

- Search for multiple angles: background, current state, key facts, recent developments
- Collect specific data points, statistics, and quotes where available
- Note the source of each key claim
- Be thorough — the analyst agent depends on your findings
"""


def build_researcher_node():
    search_tool = get_search_tool()
    tools = [search_tool]

    llm = ChatAnthropic(
        model=config.default_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.anthropic_api_key,
    ).bind_tools(tools)

    tool_node = ToolNode(tools)

    def researcher(state: ResearchState) -> ResearchState:
        messages = [SystemMessage(content=_SYSTEM_PROMPT), *list(state["messages"])]
        response = llm.invoke(messages)
        return {"messages": [response]}

    def should_use_tools(state: ResearchState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "analyst"

    return researcher, tool_node, should_use_tools
