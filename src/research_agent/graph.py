from __future__ import annotations

from langgraph.graph import StateGraph, END

from research_agent.state import ResearchState
from research_agent.agents.researcher import build_researcher_node
from research_agent.agents.retriever_agent import build_retriever_agent_node
from research_agent.agents.analyst import build_analyst_node
from research_agent.agents.synthesizer import build_synthesizer_node


def _route_after_analyst(state: ResearchState) -> str:
    return state.get("next", "synthesizer")


def build_graph():
    researcher_node, tool_node, should_use_tools = build_researcher_node()
    retriever_node = build_retriever_agent_node()
    analyst_node = build_analyst_node()
    synthesizer_node = build_synthesizer_node()

    graph = StateGraph(ResearchState)

    graph.add_node("retriever", retriever_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("research_tools", tool_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Both retriever (RAG) and researcher (web) run first, then analyst combines
    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "researcher")

    graph.add_conditional_edges(
        "researcher",
        should_use_tools,
        {"tools": "research_tools", "analyst": "analyst"},
    )
    graph.add_edge("research_tools", "researcher")

    graph.add_conditional_edges(
        "analyst",
        _route_after_analyst,
        {"synthesizer": "synthesizer"},
    )
    graph.add_edge("synthesizer", END)

    return graph.compile()
