from __future__ import annotations
from typing import Dict, Set
from ..model.graph_types import NodeId

class DepIndex:
    def __init__(self):
        self.node_to_flags: Dict[NodeId, Set[str]] = {}

    def index_flag(self, node_id: NodeId, flag: str):
        self.node_to_flags.setdefault(node_id, set()).add(flag)

    def affected_flags(self, node_id: NodeId) -> Set[str]:
        return self.node_to_flags.get(node_id, set())

    def merge(self, other: "DepIndex"):
        for n, fs in other.node_to_flags.items():
            self.node_to_flags.setdefault(n, set()).update(fs)
