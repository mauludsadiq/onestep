from onestepx_tools.cache import load, save
from onestepx_tools.ingest import load_rows
from onestepx import TERMINAL

def test_cache_load_and_types():
    load("onestepx_cache.json")
    pb = TERMINAL.flags["proj_bitsets"]
    assert set(pb.keys()) == {
        "budget_gt_5m","status_delayed","team_remote",
        "has_skill_ML","deps_gt_10","lastchg_gt_5"
    }
    assert all(isinstance(v, set) for v in pb.values())

def test_q1_matches_naive():
    rows = load_rows("./data")
    load("onestepx_cache.json")
    pb = TERMINAL.flags["proj_bitsets"]

    t = (pb["budget_gt_5m"] & pb["status_delayed"] & pb["team_remote"]
         & pb["has_skill_ML"] & pb["deps_gt_10"] & pb["lastchg_gt_5"])

    def ok(r):
        return (r.get("type")=="project"
                and r.get("budget",0) > 5_000_000
                and r.get("status")=="delayed"
                and (r.get("team",{}) or {}).get("location")=="remote"
                and "ML" in (r.get("skills") or [])
                and r.get("dependencies",0) > 10
                and r.get("audit_last_week",0) > 5)

    naive = {str(r["id"]) for r in rows if ok(r)}
    assert t == naive

def test_save_load_idempotent(tmp_path):
    # round-trip should preserve facet membership
    load("onestepx_cache.json")
    snap1 = {k: set(v) for k,v in TERMINAL.flags["proj_bitsets"].items()}
    # write to a temp file, then reload from there
    out = tmp_path/"roundtrip.json"
    save(str(out))
    load(str(out))
    snap2 = TERMINAL.flags["proj_bitsets"]
    assert {k: set(v) for k,v in snap2.items()} == snap1
