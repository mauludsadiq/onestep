from __future__ import annotations
from typing import Dict, Set, Tuple, Any
from dataclasses import dataclass

NodeId = str
Edge = Tuple[NodeId, NodeId]

@dataclass
class Node:
    id: NodeId
    attrs: Dict[str, Any]

@dataclass
class Graph:
    nodes: Dict[NodeId, Node]
    edges: Set[Edge]
    version: int
