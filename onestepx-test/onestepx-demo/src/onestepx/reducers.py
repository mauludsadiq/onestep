from collections import defaultdict
from typing import Dict, Any, Iterable, Set

# A simple reducers registry
_REGISTRY = {}

def reducer(name):
    def deco(fn):
        _REGISTRY[name] = fn
        return fn
    return deco

def available() -> Dict[str, Any]:
    return dict(_REGISTRY)

# --- Example reducers mapping Claude-style predicates into T indexes ---

@reducer("project_facets")
def project_facets(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    budget_gt_5m: Set[str] = set()
    status_delayed: Set[str] = set()
    team_remote: Set[str] = set()
    has_skill_ml: Set[str] = set()
    deps_gt_10: Set[str] = set()
    lastchg_gt_5: Set[str] = set()

    for r in records:
        if r.get("type") not in {"project","proj","p"}: 
            continue
        rid = str(r.get("id"))
        if rid == "None":
            continue
        if (r.get("budget") or 0) > 5_000_000: budget_gt_5m.add(rid)
        if r.get("status") == "delayed": status_delayed.add(rid)
        if r.get("team_loc") == "remote": team_remote.add(rid)
        if "ML" in (r.get("skills") or set()): has_skill_ml.add(rid)
        if (r.get("deps") or 0) > 10: deps_gt_10.add(rid)
        if (r.get("last_week_changes") or 0) > 5: lastchg_gt_5.add(rid)

    return {
        "proj_bitsets": {
            "budget_gt_5m": budget_gt_5m,
            "status_delayed": status_delayed,
            "team_remote": team_remote,
            "has_skill_ML": has_skill_ml,
            "deps_gt_10": deps_gt_10,
            "lastchg_gt_5": lastchg_gt_5,
        }
    }

@reducer("group_medians")
def group_medians(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    # Example: median budget by status (toy)
    buckets = defaultdict(list)
    for r in records:
        if r.get("type") in {"project","proj","p"}:
            b = r.get("budget")
            s = r.get("status") or "unknown"
            if b is not None:
                buckets[s].append(b)
    med = {k: sorted(v)[len(v)//2] for k,v in buckets.items() if v}
    return {"median_budget_by_status": med}
