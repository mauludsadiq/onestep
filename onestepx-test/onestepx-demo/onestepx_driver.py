from __future__ import annotations
import os, random
try:
    import psutil
except Exception:
    psutil = None

from onestepx import TERMINAL
from onestepx_tools.cache import load, save

_QS = ("Q1","Q2","Q3","Q4","Q5","Q6","Q7")

class Driver:
    def __init__(self, *, cache_path="onestepx_cache.json"):
        self.cache_path = cache_path
        load(self.cache_path)
        self._pb = TERMINAL.flags.get("proj_bitsets", False)
        self._snapshots = 0

    def mutate_once(self):
        pb = self._pb
        pick = next(iter(pb["lastchg_gt_5"]), "p1")
        (pb["has_skill_ML"].discard(pick)
         if pick in pb["has_skill_ML"] else pb["has_skill_ML"].add(pick))
        (pb["status_delayed"].discard(pick)
         if pick in pb["status_delayed"] else pb["status_delayed"].add(pick))
        save(self.cache_path)
        self._snapshots += 1

    def read_query(self, name: str):
        b = self._pb
        if name == "Q1":
            return (b["budget_gt_5m"] & b["status_delayed"] & b["team_remote"]
                    & b["has_skill_ML"] & b["deps_gt_10"] & b["lastchg_gt_5"])
        if name == "Q2":
            A,B,C,E,F = b["budget_gt_5m"], b["status_delayed"], b["team_remote"], b["deps_gt_10"], b["lastchg_gt_5"]
            return ((A & B) | (C & E)) & F
        if name == "Q3":
            A,B,C,D,E,F = b["budget_gt_5m"], b["status_delayed"], b["team_remote"], b["has_skill_ML"], b["deps_gt_10"], b["lastchg_gt_5"]
            return (A | B | C) & (D | E | F)
        if name == "Q4":
            A,B,D = b["budget_gt_5m"], b["status_delayed"], b["has_skill_ML"]
            return (A & B) - D
        if name == "Q5":
            return b["budget_gt_5m"] & b["status_delayed"] & b["team_remote"] & b["deps_gt_10"]
        if name == "Q6":
            return (b["budget_gt_5m"] | b["status_delayed"] | b["team_remote"]
                    | b["has_skill_ML"] | b["deps_gt_10"] | b["lastchg_gt_5"])
        if name == "Q7":
            A,B,C,D,E,F = b["budget_gt_5m"], b["status_delayed"], b["team_remote"], b["has_skill_ML"], b["deps_gt_10"], b["lastchg_gt_5"]
            return (((A & B) | (C & D)) & E) - F
        raise ValueError(f"unknown query {name}")

    def list_queries(self):
        return list(_QS)

    def snapshot_count(self) -> int:
        return self._snapshots

    def memory_bytes(self):
        if psutil:
            try:
                return psutil.Process(os.getpid()).memory_info().rss
            except Exception:
                pass
        return None

    def tenant_new(self, tenant_id: str):
        return self

def init_driver(**kwargs):
    return Driver(**kwargs)
