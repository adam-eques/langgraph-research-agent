from __future__ import annotations

from langgraph.graph import StateGraph, END

from research_agent.state import ResearchState
from research_agent.agents.researcher import build_researcher_node
from research_agent.agents.analyst import build_analyst_node
from research_agent.agents.synthesizer import build_synthesizer_node


def build_graph():
    researcher_node, tool_node, should_use_tools = build_researcher_node()
    analyst_node = build_analyst_node()
    synthesizer_node = build_synthesizer_node()

    graph = StateGraph(ResearchState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("research_tools", tool_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("researcher")

    graph.add_conditional_edges(
        "researcher",
        should_use_tools,
        {"tools": "research_tools", "analyst": "analyst"},
    )
    graph.add_edge("research_tools", "researcher")
    graph.add_edge("analyst", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
