from onestepx import TERMINAL

def seed_default_flags():
    # attach a minimal proj_bitsets table for demos/bench
    TERMINAL.flags = {"proj_bitsets": {
        "team_remote":    set(range(0, 200_000, 3)),
        "status_delayed": set(range(0, 200_000, 5)),
        "has_skill_ml":   set(range(0, 200_000, 7)),
    }}
    return TERMINAL.flags
