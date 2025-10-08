from collections import defaultdict
from typing import Dict, Any, Iterable, Set

_REGISTRY = {}

def reducer(name):
    def deco(fn):
        _REGISTRY[name] = fn
        return fn
    return deco

def available() -> Dict[str, Any]:
    return dict(_REGISTRY)

@reducer("project_facets")
def project_facets(records):
    budget_gt_5m, status_delayed, team_remote = set(), set(), set()
    has_skill_ml, deps_gt_10, lastchg_gt_5 = set(), set(), set()
    for r in records:
        if r.get("type") not in {"project","proj","p"}:
            continue
        pid = str(r.get("id"))
        if pid == "None":
            continue

        budget = r.get("budget", 0)
        status = r.get("status")
        team_loc = (r.get("team") or {}).get("location") or r.get("team_loc")
        skills  = r.get("skills") or []
        deps    = r.get("dependencies", r.get("deps", 0)) or 0
        lastwk  = r.get("audit_last_week", r.get("last_week_changes", 0)) or 0

        if budget > 5_000_000:               budget_gt_5m.add(pid)
        if status == "delayed":               status_delayed.add(pid)
        if team_loc == "remote":              team_remote.add(pid)
        if "ML" in (skills if isinstance(skills,(list,set,tuple)) else []): has_skill_ml.add(pid)
        if deps > 10:                         deps_gt_10.add(pid)
        if lastwk > 5:                        lastchg_gt_5.add(pid)

    return {"proj_bitsets": {
        "budget_gt_5m": budget_gt_5m,
        "status_delayed": status_delayed,
        "team_remote": team_remote,
        "has_skill_ML": has_skill_ml,
        "deps_gt_10": deps_gt_10,
        "lastchg_gt_5": lastchg_gt_5}}

@reducer("group_medians")
def group_medians(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    buckets = defaultdict(list)
    for r in records:
        if r.get("type") in {"project","proj","p"}:
            b = r.get("budget")
            s = r.get("status") or "unknown"
            if b is not None:
                buckets[s].append(b)
    med = {k: sorted(v)[len(v)//2] for k,v in buckets.items() if v}
    return {"median_budget_by_status": med}

from statistics import median

def facet_by_team_and_skill(rows):
    team_remote = set()
    has_skill_cloud = set()
    for r in rows:
        if r.get("type") != "project":
            continue
        pid = r["id"]
        if r.get("team", {}).get("location") == "remote":
            team_remote.add(pid)
        if "Cloud" in r.get("skills", []):
            has_skill_cloud.add(pid)
    return {"team_remote": team_remote, "has_skill_Cloud": has_skill_cloud}

def costs_since(rows, iso_date="2024-01-01"):
    # sum project budgets for items allocated after a given date
    # (demo: treat audit_last_week>0 as "after date")
    total = 0
    for r in rows:
        if r.get("type") != "project":
            continue
        if r.get("audit_last_week", 0) > 0:
            total += int(r.get("budget", 0))
    return {"sum_costs_after_cutoff": total}

def naive_cycle_present(rows):
    # demo “cycle” boolean (no traversal): True if any project has >10 deps
    return {"cycles_present": any(r.get("dependencies", 0) > 10
                                  for r in rows if r.get("type")=="project")}

def register_more(reducers):
    reducers["proj_bitsets"].update(facet_by_team_and_skill)
    reducers["time_costs"] = costs_since
    reducers["graph_signals"] = naive_cycle_present

from statistics import median

def facet_by_team_and_skill(rows):
    team_remote = set()
    has_skill_cloud = set()
    for r in rows:
        if r.get("type") != "project":
            continue
        pid = r["id"]
        if r.get("team", {}).get("location") == "remote":
            team_remote.add(pid)
        if "Cloud" in r.get("skills", []):
            has_skill_cloud.add(pid)
    return {"team_remote": team_remote, "has_skill_Cloud": has_skill_cloud}

def costs_since(rows, iso_date="2024-01-01"):
    total = 0
    for r in rows:
        if r.get("type") != "project":
            continue
        if r.get("audit_last_week", 0) > 0:
            total += int(r.get("budget", 0))
    return {"sum_costs_after_cutoff": total}

def naive_cycle_present(rows):
    return {"cycles_present": any(
        r.get("type") == "project" and r.get("dependencies", 0) > 10
        for r in rows
    )}

def register_more(reducers_dict):
    reducers_dict["time_costs"] = costs_since
    reducers_dict["graph_signals"] = naive_cycle_present
    # also extend the existing proj_bitsets with extra facets:
    # the builder will merge this into flags["proj_bitsets"] if present
    reducers_dict["proj_bitsets_extra"] = facet_by_team_and_skill

# alias for back-compat
try:
    project_bitsets
except NameError:
    project_bitsets = project_facets

from statistics import median
def median_budget_by_status(rows):
    buckets = {}
    for r in rows:
        status = r.get('status')
        budget = r.get('budget')
        if status is None or budget is None:
            continue
        buckets.setdefault(status, []).append(budget)
    return {k: median(v) for k, v in buckets.items() if v}
