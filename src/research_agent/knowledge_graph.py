from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KGNode:
    id: str
    label: str
    node_type: str = "entity"
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class KGEdge:
    source_id: str
    target_id: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, KGNode] = {}
        self._edges: list[KGEdge] = []

    def add_node(self, node: KGNode) -> None:
        self._nodes[node.id] = node

    def add_edge(self, edge: KGEdge) -> None:
        if edge.source_id in self._nodes and edge.target_id in self._nodes:
            self._edges.append(edge)

    def get_node(self, node_id: str) -> KGNode | None:
        return self._nodes.get(node_id)

    def neighbors(self, node_id: str) -> list[str]:
        result = []
        for e in self._edges:
            if e.source_id == node_id:
                result.append(e.target_id)
            elif e.target_id == node_id:
                result.append(e.source_id)
        return list(set(result))

    def find_path(self, start: str, end: str) -> list[str] | None:
        visited: set[str] = set()
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == end:
                return path
            if node in visited:
                continue
            visited.add(node)
            for neighbor in self.neighbors(node):
                queue.append([*path, neighbor])
        return None

    def to_dict(self) -> dict:
        return {
            "nodes": [
                {"id": n.id, "label": n.label, "type": n.node_type} for n in self._nodes.values()
            ],
            "edges": [
                {"src": e.source_id, "tgt": e.target_id, "rel": e.relation} for e in self._edges
            ],
        }

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)
