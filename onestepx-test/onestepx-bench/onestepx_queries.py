import time
from onestepx import TERMINAL

def _pb():
    return TERMINAL.flags["proj_bitsets"]

def big_delayed_remote_ml_manydeps_recent():
    pb = _pb()
    s = (pb["budget_gt_5m"]
         & pb["status_delayed"]
         & pb["team_remote"]
         & pb["has_skill_ml"]
         & pb["deps_gt_10"]
         & pb["audit_last_week_gt_5"])
    return s

def any_critical_remote_exclude_lowdeps():
    pb = _pb()
    s = (pb["status_delayed"] & pb["team_remote"]) - pb["deps_gt_10"]
    return s

def and_chain(keys):
    pb = _pb()
    it = iter(keys)
    base = pb[next(it)].copy()
    for k in it:
        base &= pb[k]
    return base

def or_chain(keys):
    pb = _pb()
    out = set()
    for k in keys:
        out |= pb[k]
    return out

def timed(fn, *args, repeat=5, **kwargs):
    best = None
    val = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        val = fn(*args, **kwargs)
        dt = (time.perf_counter() - t0) * 1e3
        best = dt if best is None else min(best, dt)
    return val, best

def seed_costs_if_missing():
    if "costs" in TERMINAL.flags:
        return
    # attach a cheap cost per project id (demo)
    costs = {}
    for k in big_delayed_remote_ml_manydeps_recent():
        costs[k] = (k % 1000) * 1.23
    TERMINAL.flags["costs"] = costs

def sum_costs_over(s):
    costs = TERMINAL.flags.get("costs", {})
    return sum(costs.get(k, 0.0) for k in s)
