from __future__ import annotations
from typing import Dict, Set
from ..model.graph_types import Graph, Node, NodeId
from ..model.terminal import Terminal
from .depindex import DepIndex

def _outdegree_table(G: Graph) -> Dict[NodeId, int]:
    od: Dict[NodeId, int] = {n:0 for n in G.nodes}
    for u, v in G.edges:
        if u in od:
            od[u] += 1
    return od

def derive_flags_for_node(G: Graph, n: NodeId, outdeg_cache: Dict[NodeId,int] | None = None) -> Set[str]:
    node = G.nodes[n]
    attrs = node.attrs or {}
    flags: Set[str] = set()
    div = attrs.get("division")
    if isinstance(div, str):
        flags.add(f"division:{div}")
    skills = attrs.get("skills", [])
    if isinstance(skills, (list, tuple, set)):
        for s in skills:
            flags.add(f"skill:{s}")
    budget = attrs.get("budget")
    if isinstance(budget, (int, float)) and budget > 5_000_000:
        flags.add("over_budget")
    k = 10
    if outdeg_cache is None:
        outdeg_cache = _outdegree_table(G)
    if outdeg_cache.get(n, 0) > k:
        flags.add("deps>10")
    return flags

def full_rebuild(G: Graph) -> tuple[Terminal, DepIndex]:
    T = Terminal(flags={}, summaries={}, version=G.version)
    dep = DepIndex()
    od = _outdegree_table(G)
    for n in G.nodes:
        derived = derive_flags_for_node(G, n, od)
        for f in derived:
            T.flags.setdefault(f, set()).add(n)
            dep.index_flag(n, f)
    return T, dep
