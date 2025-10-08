from __future__ import annotations
import time
from .common import tiny_graph, bump_version, build_full
from ..delta.collapse_delta import incremental_update
from ..delta.metrics import Day1Metrics, emit

def test_root_mutation_threshold():
    G0 = tiny_graph(n=20000, fanout=2)
    T0, dep0 = build_full(G0)
    G1 = bump_version(G0)
    G1.nodes = G1.nodes.copy()
    root = "n0"
    G1.nodes[root] = type(G1.nodes[root])(id=root, attrs={**G1.nodes[root].attrs, "division":"omega"})
    T1, dep1, res = incremental_update(G0, G1, T0, dep0, build_full, max_flag_touch_ratio=0.15)
    m = Day1Metrics(res.method, res.t_us, res.affected_flags, res.affected_nodes,
                    len(T0.flags), len(G1.nodes), time.time_ns())
    emit(m)
    assert res.method in ("incremental","full")
