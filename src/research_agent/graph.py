from __future__ import annotations

from langgraph.graph import StateGraph, END

from research_agent.state import ResearchState


def _placeholder_node(state: ResearchState) -> ResearchState:
    return state


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)
    graph.add_node("researcher", _placeholder_node)
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", END)
    return graph.compile()
