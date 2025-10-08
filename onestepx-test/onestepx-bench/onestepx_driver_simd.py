import numpy as np
from onestepx_driver_seeded import init_driver as seeded_init
from onestepx_fast import build_bitplanes_from_sets, warmup, and_not, k_and, k_or, popcount_u8

class SIMDDriver:
    def __init__(self, base_drv=None):
        self.base = base_drv or seeded_init()
        qs = {q: self.base.read_query(q) for q in self.base.list_queries()}

        alias = {
            "budget_gt_5m": "Q1",
            "has_skill_ml": "Q2",
            "audit_last_week_gt_5": "Q3",
            "status_delayed": "Q4",
            "team_remote": "Q5",
            "deps_gt_10": "Q6",
        }
        # keep only those present
        sets_map = {k: qs[v] for k, v in alias.items() if v in qs}

        # ===== dynamic N from actual ids =====
        max_id = 0
        for s in sets_map.values():
            if s:
                m = max(s)
                if m > max_id:
                    max_id = m
        self.N = max_id + 1 if max_id >= 0 else 0

        self.bp = build_bitplanes_from_sets(sets_map, self.N)
        warmup(self.bp)

    def hot_and(self):
        return and_not(self.bp["team_remote"], self.bp["status_delayed"], self.bp["deps_gt_10"])

    def complex_AND(self):
        return k_and([self.bp["budget_gt_5m"], self.bp["has_skill_ml"], self.bp["audit_last_week_gt_5"]])

    def any_OR(self):
        return k_or([self.bp["status_delayed"], self.bp["team_remote"], self.bp["deps_gt_10"]])

    def count(self, arr_u8):
        return int(popcount_u8(arr_u8))
