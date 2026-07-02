from __future__ import annotations

from research_agent.knowledge_graph import KGEdge, KGNode, KnowledgeGraph


def make_graph() -> KnowledgeGraph:
    kg = KnowledgeGraph()
    kg.add_node(KGNode("1", "Python"))
    kg.add_node(KGNode("2", "ML"))
    kg.add_node(KGNode("3", "AI"))
    kg.add_edge(KGEdge("1", "2", "used_for"))
    kg.add_edge(KGEdge("2", "3", "subset_of"))
    return kg


def test_add_and_get():
    kg = make_graph()
    assert kg.get_node("1").label == "Python"


def test_neighbors():
    kg = make_graph()
    assert "2" in kg.neighbors("1")


def test_find_path():
    kg = make_graph()
    path = kg.find_path("1", "3")
    assert path == ["1", "2", "3"]


def test_to_dict():
    kg = make_graph()
    d = kg.to_dict()
    assert len(d["nodes"]) == 3 and len(d["edges"]) == 2


def test_counts():
    kg = make_graph()
    assert kg.node_count == 3 and kg.edge_count == 2
