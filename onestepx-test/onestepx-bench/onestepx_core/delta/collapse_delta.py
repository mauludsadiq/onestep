from __future__ import annotations
import time
from typing import Set
from .diffing import diff_graph
from .depindex import DepIndex
from ..model.terminal import Terminal
from ..model.graph_types import Graph, NodeId
from .full_build import derive_flags_for_node

class DeltaResult:
    def __init__(self, method:str, t_us:int, affected_flags:int, affected_nodes:int):
        self.method = method
        self.t_us = t_us
        self.affected_flags = affected_flags
        self.affected_nodes = affected_nodes

def _collect_affected_nodes(G_old: Graph, G_new: Graph, d) -> Set[NodeId]:
    affected = set(d.added_nodes | d.removed_nodes | d.changed_nodes)
    affected |= {u for (u,_) in d.added_edges | d.removed_edges}
    affected |= {v for (_,v) in d.added_edges | d.removed_edges}
    return affected

def incremental_update(G_old: Graph, G_new: Graph, T_old: Terminal, dep: DepIndex,
                       full_rebuild_fn,          # Φ build function: Graph -> (Terminal, DepIndex)
                       max_flag_touch_ratio=0.15  # fallback threshold
                      ) -> (Terminal, DepIndex, DeltaResult):
    t0 = time.time_ns()
    delta = diff_graph(G_old, G_new)
    affected_nodes = _collect_affected_nodes(G_old, G_new, delta)

    # Only consider flags that actually CHANGE for the affected nodes
    flags_to_recompute = set()
    for n in affected_nodes:
        oldf = derive_flags_for_node(G_old, n) if n in G_old.nodes else set()
        newf = derive_flags_for_node(G_new, n) if n in G_new.nodes else set()
        flags_to_recompute |= (oldf ^ newf)

    total_flags = max(len(T_old.flags), 1)

    # Dynamic threshold: be more permissive for tiny flag spaces
    if total_flags <= 10:
        dynamic_thresh = 0.8
    elif total_flags <= 20:
        dynamic_thresh = 0.25
    else:
        dynamic_thresh = max_flag_touch_ratio

    touch_ratio = len(flags_to_recompute) / total_flags
    if touch_ratio > dynamic_thresh:
        T_new, dep_new = full_rebuild_fn(G_new)
        t_us = (time.time_ns() - t0)//1000
        return T_new, dep_new, DeltaResult("full", t_us, total_flags, len(affected_nodes))

    # Localized recompute: copy untouched flags; clear touched ones
    T_new = Terminal(flags={k: (set(v) if k not in flags_to_recompute else set())
                             for k, v in T_old.flags.items()},
                     summaries=T_old.summaries.copy(),
                     version=G_new.version)

    # Recompute only for affected nodes
    for n in affected_nodes:
        node = G_new.nodes.get(n)
        if node is None:
            # removal: ensure n is not in any recomputed flag
            for f in flags_to_recompute:
                T_new.flags.setdefault(f, set()).discard(n)
            continue

        derived = derive_flags_for_node(G_new, n)
        for f in derived:
            if f in flags_to_recompute:
                T_new.flags.setdefault(f, set()).add(n)

    # Refresh dep index only for affected nodes
    dep_new = dep
    for n in affected_nodes:
        derived = derive_flags_for_node(G_new, n) if n in G_new.nodes else set()
        for f in derived:
            dep_new.index_flag(n, f)

    t_us = (time.time_ns() - t0)//1000
    return T_new, dep_new, DeltaResult("incremental", t_us, len(flags_to_recompute), len(affected_nodes))
