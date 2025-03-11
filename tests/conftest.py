from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from research_agent.state import ResearchState


@pytest.fixture
def base_state() -> ResearchState:
    return {
        "messages": [HumanMessage(content="What is LangGraph?")],
        "query": "What is LangGraph?",
        "research_notes": [],
        "document_context": "",
        "next": "",
    }
