from __future__ import annotations

# PATCH: Node.flags workaround for Python 3.12
try:
    # Ensure Node instances always have .flags
    from onestepx.hierarchy import Node
    if not hasattr(Node, "__orig_init__"):
        Node.__orig_init__ = Node.__init__
        def __init__(self, *a, **kw):
            Node.__orig_init__(self, *a, **kw)
            if not hasattr(self, "flags"):
                self.flags = {}
        Node.__init__ = __init__

    # Ensure TERMINAL.flags exists
    from onestepx import TERMINAL
    if not hasattr(TERMINAL, "flags"):
        TERMINAL.flags = {}
except Exception as e:
    import sys
    print("⚠️ Node/TERMINAL flags prepatch failed:", e, file=sys.stderr)
# END PATCH


try:
    from onestepx.hierarchy import Node
    if not hasattr(Node, "__orig_init__"):
        Node.__orig_init__ = Node.__init__
        def __init__(self, *a, **kw):
            Node.__orig_init__(self, *a, **kw)
            if not hasattr(self, "flags"):
                self.flags = {}
        Node.__init__ = __init__
    print("✅ onestepx_driver_seeded: Node.flags prepatch applied")
except Exception as e:
    import sys; print("⚠️ Node.flags prepatch failed:", e, file=sys.stderr)


### prepatch Node.flags
try:
    from onestepx.hierarchy import Node
    if not hasattr(Node, "__orig_init__"):
        Node.__orig_init__ = Node.__init__
        def __init__(self, *a, **kw):
            Node.__orig_init__(self, *a, **kw)
            if not hasattr(self, "flags"):
                self.flags = {}
        Node.__init__ = __init__
    print("✅ onestepx_driver_seeded: Node.flags prepatch applied")
except Exception as e:
    import sys; print("⚠️ Node.flags prepatch failed:", e, file=sys.stderr)
### end prepatch Node.flags
import onestepx_driver as _base
import random
import datetime as dt
from onestepx import TERMINAL
from onestepx_tools.cache import load

def _init_all_flags():
    """Initialize all required TERMINAL.flags with seeded random data"""
    rng = random.Random(7)
    N_PROJ = 20000
    N_ALLOC = 50000
    
    # Project bitsets
    if "proj_bitsets" not in TERMINAL.flags:
        budget_gt_5m = set()
        status_delayed = set()
        team_remote = set()
        has_skill_ML = set()
        deps_gt_10 = set()
        lastchg_gt_5 = set()
        
        for i in range(N_PROJ):
            if rng.randrange(1_000_000, 10_000_000) > 5_000_000:
                budget_gt_5m.add(i)
            if rng.choice(["ok","delayed","critical"]) == "delayed":
                status_delayed.add(i)
            if rng.choice(["onsite","remote","hybrid"]) == "remote":
                team_remote.add(i)
            skills = set(rng.sample(["ML","FE","BE","Cloud","Security"], rng.randrange(1,4)))
            if "ML" in skills:
                has_skill_ML.add(i)
            if rng.randrange(0, 30) > 10:
                deps_gt_10.add(i)
            if rng.randrange(0, 12) > 5:
                lastchg_gt_5.add(i)
        
        # Store in nested dict for driver compatibility
        TERMINAL.flags["proj_bitsets"] = {
            "budget_gt_5m": budget_gt_5m,
            "status_delayed": status_delayed,
            "team_remote": team_remote,
            "has_skill_ML": has_skill_ML,
            "has_skill_ml": has_skill_ML,
            "deps_gt_10": deps_gt_10,
            "lastchg_gt_5": lastchg_gt_5,
            "audit_last_week_gt_5": lastchg_gt_5,
        }
        
        # ALSO store at top level for scripts that expect flat access
        TERMINAL.flags["budget_gt_5m"] = budget_gt_5m
        TERMINAL.flags["status_delayed"] = status_delayed
        TERMINAL.flags["team_remote"] = team_remote
        TERMINAL.flags["has_skill_ml"] = has_skill_ML
        TERMINAL.flags["deps_gt_10"] = deps_gt_10
        TERMINAL.flags["audit_last_week_gt_5"] = lastchg_gt_5
    
    # Allocation timestamps and costs
    if "alloc_ts" not in TERMINAL.flags:
        base = dt.datetime(2024, 1, 1)
        alloc_ts = {}
        costs = {}
        for r in range(N_ALLOC):
            cost = rng.randrange(100, 50_000)
            ts = base + dt.timedelta(days=rng.randrange(0, 700))
            alloc_ts[r] = ts
            costs[r] = cost
        
        TERMINAL.flags["alloc_ts"] = alloc_ts
        TERMINAL.flags["costs"] = costs
    
    # Cycles
    if "in_cycles" not in TERMINAL.flags:
        cycle_node_ratio = 0.03
        in_cycles = set(rng.sample(range(N_PROJ), int(N_PROJ * cycle_node_ratio)))
        TERMINAL.flags["in_cycles"] = in_cycles
    
    # Project divisions
    if "proj_division" not in TERMINAL.flags:
        divisions = ["Engineering", "Sales", "G&A", "Design"]
        proj_division = {i: rng.choice(divisions) for i in range(N_PROJ)}
        TERMINAL.flags["proj_division"] = proj_division

class Driver(_base.Driver):
    def __init__(self, *, cache_path="onestepx_cache.json"):
        self.cache_path = cache_path
        load(self.cache_path)
        _init_all_flags()
        self._pb = TERMINAL.flags.get("proj_bitsets", False)
        self._snapshots = 0

def init_driver(**kwargs):
    return Driver(**kwargs)
