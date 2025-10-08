from onestepx import TERMINAL
TERMINAL.flags = getattr(TERMINAL, "flags", {})
TERMINAL.flags["proj_bitsets"] = {
    "budget_gt_5m": set(range(0, 200_000, 2)),
    "status_delayed": set(range(50_000, 250_000)),
    "team_remote": set(range(0, 300_000, 3)),
    "has_skill_ml": set(range(0, 400_000, 5)),
    "deps_gt_10": set(range(10_000, 210_000)),
    "audit_last_week_gt_5": set(range(0, 500_000, 7)),
}
