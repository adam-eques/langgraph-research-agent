from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from research_agent.state import ResearchState
from research_agent.agents.researcher import build_researcher_node
from research_agent.agents.retriever_agent import build_retriever_agent_node
from research_agent.agents.analyst import build_analyst_node
from research_agent.agents.synthesizer import build_synthesizer_node
from research_agent.agents.supervisor import build_supervisor_node


def build_graph(checkpointing: bool = False, use_supervisor: bool = False):
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

    if use_supervisor:
        supervisor_node, supervisor_route = build_supervisor_node()
        graph.add_node("supervisor", supervisor_node)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges(
            "supervisor",
            supervisor_route,
            {
                "retriever": "retriever",
                "researcher": "researcher",
                "analyst": "analyst",
                "synthesizer": "synthesizer",
                "end": END,
            },
        )
        for node in ("retriever", "analyst", "synthesizer"):
            graph.add_edge(node, "supervisor")
        graph.add_conditional_edges(
            "researcher",
            should_use_tools,
            {"tools": "research_tools", "analyst": "supervisor"},
        )
        graph.add_edge("research_tools", "researcher")
    else:
        graph.set_entry_point("retriever")
        graph.add_edge("retriever", "researcher")
        graph.add_conditional_edges(
            "researcher",
            should_use_tools,
            {"tools": "research_tools", "analyst": "analyst"},
        )
        graph.add_edge("research_tools", "researcher")
        graph.add_edge("analyst", "synthesizer")
        graph.add_edge("synthesizer", END)

    checkpointer = MemorySaver() if checkpointing else None
    return graph.compile(checkpointer=checkpointer)


def get_graph_visualization() -> str:
    """Return a Mermaid diagram string of the compiled graph."""
    return build_graph().get_graph().draw_mermaid()


def get_graph_png(output_path: str = "graph.png") -> None:
    """Save the graph as a PNG image (requires graphviz)."""
    img = build_graph().get_graph().draw_mermaid_png()
    with open(output_path, "wb") as f:
        f.write(img)
