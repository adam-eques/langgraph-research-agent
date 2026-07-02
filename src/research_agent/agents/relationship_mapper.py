from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Relationship:
    subject: str
    predicate: str
    obj: str
    confidence: float = 1.0
    source: str = ""


@dataclass
class EntityGraph:
    nodes: set[str] = field(default_factory=set)
    edges: list[Relationship] = field(default_factory=list)

    def add_relationship(self, rel: Relationship) -> None:
        self.nodes.add(rel.subject)
        self.nodes.add(rel.obj)
        self.edges.append(rel)

    def neighbors(self, entity: str) -> list[str]:
        result = []
        for e in self.edges:
            if e.subject == entity:
                result.append(e.obj)
            elif e.obj == entity:
                result.append(e.subject)
        return list(set(result))

    def to_dict(self) -> dict:
        return {
            "nodes": list(self.nodes),
            "edges": [
                {"subject": e.subject, "predicate": e.predicate, "object": e.obj, "confidence": e.confidence}
                for e in self.edges
            ],
        }


_RELATION_PATTERNS = [
    (r"(\w+)\s+is\s+a\s+(\w+)", "is-a"),
    (r"(\w+)\s+uses\s+(\w+)", "uses"),
    (r"(\w+)\s+extends\s+(\w+)", "extends"),
    (r"(\w+)\s+depends\s+on\s+(\w+)", "depends-on"),
    (r"(\w+)\s+implements\s+(\w+)", "implements"),
]


def extract_relationships(text: str) -> list[Relationship]:
    rels = []
    for pattern, predicate in _RELATION_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            rels.append(Relationship(subject=m.group(1), predicate=predicate, obj=m.group(2)))
    return rels


def build_entity_graph(texts: list[str]) -> EntityGraph:
    graph = EntityGraph()
    for text in texts:
        for rel in extract_relationships(text):
            graph.add_relationship(rel)
    return graph
