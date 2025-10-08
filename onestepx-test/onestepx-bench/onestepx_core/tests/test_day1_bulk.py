from __future__ import annotations
import time, random
from .common import tiny_graph, bump_version, build_full
from ..delta.collapse_delta import incremental_update
from ..delta.metrics import Day1Metrics, emit

def test_bulk_100_nodes():
    random.seed(0)
    G0 = tiny_graph(n=30000, fanout=2)
    T0, dep0 = build_full(G0)
    G1 = bump_version(G0)
    G1.nodes = G1.nodes.copy()
    picks = random.sample(list(G1.nodes.keys()), 100)
    for pid in picks:
        node = G1.nodes[pid]
        G1.nodes[pid] = type(node)(id=pid, attrs={**node.attrs, "budget": (node.attrs.get("budget",0) + 6_000_000)})
    T1, dep1, res = incremental_update(G0, G1, T0, dep0, build_full, max_flag_touch_ratio=0.5)
    m = Day1Metrics(res.method, res.t_us, res.affected_flags, res.affected_nodes,
                    len(T0.flags), len(G1.nodes), time.time_ns())
    emit(m)
    assert res.method in ("incremental","full")
