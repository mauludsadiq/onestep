import time
from onestepx import TERMINAL

def _pb(): return TERMINAL.flags["proj_bitsets"]

def predicate_A():
    pb = _pb()
    return (pb["budget_gt_5m"] & pb["status_delayed"] & pb["team_remote"]
            & pb["has_skill_ml"] & pb["deps_gt_10"] & pb["audit_last_week_gt_5"])

def temporal_window(s, ts_min=None, ts_max=None):
    ts = TERMINAL.flags["alloc_ts"]
    out = set()
    add = out.add
    if ts_min is None: ts_min = -10**18
    if ts_max is None: ts_max =  10**18
    for k in s:
        t = ts.get(k)
        if t is not None and ts_min <= t <= ts_max:
            add(k)
    return out

def in_cycles_only(s):
    cyc = TERMINAL.flags["in_cycles"]
    return s & cyc

def sum_costs(s):
    costs = TERMINAL.flags["costs"]
    return sum(costs.get(k, 0.0) for k in s)

def groupby_division_sum_costs(s):
    div = TERMINAL.flags["proj_division"]
    costs = TERMINAL.flags["costs"]
    out = {}
    for k in s:
        d = div.get(k)
        if d is None: 
            continue
        out[d] = out.get(d, 0.0) + costs.get(k, 0.0)
    return out

def timed(fn, *args, repeat=5, **kw):
    best = None; val = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        val = fn(*args, **kw)
        dt = (time.perf_counter() - t0) * 1e3
        best = dt if best is None else min(best, dt)
    return val, best
