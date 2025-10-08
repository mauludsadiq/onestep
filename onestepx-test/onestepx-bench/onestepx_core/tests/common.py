from __future__ import annotations
from ..model.graph_types import Graph, Node
from ..delta.full_build import full_rebuild

def tiny_graph(n=1000, fanout=2) -> Graph:
    nodes = {f"n{i}": Node(id=f"n{i}", attrs={"division": "alpha", "budget": i*1000, "skills": ["ML"] if i%7==0 else []}) for i in range(n)}
    edges = set()
    for i in range(n):
        for j in range(1, fanout+1):
            k = i*fanout + j
            if k < n:
                edges.add((f"n{i}", f"n{k}"))
    return Graph(nodes=nodes, edges=edges, version=1)

def bump_version(G: Graph) -> Graph:
    return Graph(nodes=G.nodes.copy(), edges=G.edges.copy(), version=G.version+1)

def build_full(G: Graph):
    return full_rebuild(G)
