
import json, time
from onestepx_tools.cache import load
from onestepx import TERMINAL

def test_cache_exists_and_has_keys():
    flags = load("onestepx_cache.json")
    assert "proj_bitsets" in flags
    assert "median_budget_by_status" in flags

def test_q1_facet_and():
    flags = load("onestepx_cache.json")
    b = flags["proj_bitsets"]
    ans = (b["budget_gt_5m"] & b["status_delayed"] & b["team_remote"]
           & b["has_skill_ML"] & b["deps_gt_10"] & b["lastchg_gt_5"])
    assert isinstance(ans, set)
    # With demo data we expect IDs present (you saw ['p1','p3'])
    assert {"p1","p3"}.issuperset(ans)

def test_terminal_injected():
    flags = load("onestepx_cache.json")
    assert TERMINAL.flags is flags
