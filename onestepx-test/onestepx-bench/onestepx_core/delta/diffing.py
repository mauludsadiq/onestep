from __future__ import annotations
from typing import Set
from ..model.graph_types import Graph, NodeId, Edge

class GraphDelta:
    def __init__(self, added_nodes:Set[NodeId], removed_nodes:Set[NodeId],
                 changed_nodes:Set[NodeId], added_edges:Set[Edge], removed_edges:Set[Edge]):
        self.added_nodes = added_nodes
        self.removed_nodes = removed_nodes
        self.changed_nodes = changed_nodes
        self.added_edges = added_edges
        self.removed_edges = removed_edges

def diff_graph(G_old: Graph, G_new: Graph) -> GraphDelta:
    old_ids, new_ids = set(G_old.nodes), set(G_new.nodes)
    added_nodes = new_ids - old_ids
    removed_nodes = old_ids - new_ids
    common = old_ids & new_ids
    changed_nodes = {n for n in common if G_old.nodes[n].attrs != G_new.nodes[n].attrs}
    added_edges = G_new.edges - G_old.edges
    removed_edges = G_old.edges - G_new.edges
    return GraphDelta(added_nodes, removed_nodes, changed_nodes, added_edges, removed_edges)
