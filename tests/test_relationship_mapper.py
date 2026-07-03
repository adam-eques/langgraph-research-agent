from __future__ import annotations

from research_agent.agents.relationship_mapper import (
    EntityGraph,
    Relationship,
    build_entity_graph,
    extract_relationships,
)


def test_extract_is_a():
    rels = extract_relationships("LangGraph is a framework.")
    assert any(r.predicate == "is-a" for r in rels)


def test_extract_uses():
    rels = extract_relationships("Python uses asyncio for concurrency.")
    assert any(r.predicate == "uses" for r in rels)


def test_build_graph():
    texts = ["Redis uses hashing.", "Redis implements caching."]
    graph = build_entity_graph(texts)
    assert "Redis" in graph.nodes


def test_neighbors():
    g = EntityGraph()
    g.add_relationship(Relationship("A", "uses", "B"))
    g.add_relationship(Relationship("A", "uses", "C"))
    assert set(g.neighbors("A")) == {"B", "C"}


def test_graph_to_dict():
    g = EntityGraph()
    g.add_relationship(Relationship("X", "extends", "Y"))
    d = g.to_dict()
    assert "nodes" in d and "edges" in d
