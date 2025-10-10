
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Iterable
import json

_EXPECTED = {
    "budget_gt_5m","status_delayed","team_remote",
    "has_skill_ML","deps_gt_10","lastchg_gt_5"
}

_ALIAS = {
    "has_skill_ml": "has_skill_ML",
    "audit_last_week_gt_5": "lastchg_gt_5",
}

def _as_path(p: str | Path) -> Path:
    return p if isinstance(p, Path) else Path(p)

def _lists_to_sets(pb: Dict[str, Any]) -> Dict[str, set]:
    out: Dict[str, set] = {}
    for k, v in pb.items():
        tgt = _ALIAS.get(k, k)
        s = set(v) if isinstance(v, (list, tuple, set)) else set()
        if tgt in out:
            out[tgt] |= s
        else:
            out[tgt] = s
    # keep only expected keys if present
    if any(k in out for k in _EXPECTED):
        out = {k: out.get(k, set()) for k in _EXPECTED}
    return out

def load(path: str | Path) -> Dict[str, Any]:
    p = _as_path(path)
    obj: Dict[str, Any] = json.loads(p.read_text())
    pb_in = obj.get("proj_bitsets", {})
    pb_sets = _lists_to_sets(pb_in)
    obj["proj_bitsets"] = pb_sets

    # Inject into onestepx.TERMINAL.flags by reference
    try:
        import onestepx
        # Ensure Node.flags exists and is a dict
        if not hasattr(onestepx, "TERMINAL") or onestepx.TERMINAL is None:
            pass
        else:
            onestepx.TERMINAL.flags = obj
    except Exception:
        # non-fatal
        pass
    return obj

def _sets_to_lists(o: Any) -> Any:
    if isinstance(o, set):
        return sorted(o)
    if isinstance(o, dict):
        return {k: _sets_to_lists(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [ _sets_to_lists(v) for v in o ]
    return o

def save(*args, **kwargs) -> Path:
    """
    save(data, path) | save(path, data) | save(path)  # uses onestepx.TERMINAL.flags
    """
    data = kwargs.get("data")
    path = kwargs.get("path")

    if len(args) == 1 and path is None and data is None:
        # save(path) → use TERMINAL.flags
        path = args[0]
        try:
            import onestepx
            data = onestepx.TERMINAL.flags
        except Exception as e:
            raise TypeError("save(path) requires onestepx.TERMINAL.flags to be available") from e
    elif len(args) == 2 and path is None and data is None:
        a,b = args
        # Detect which is which
        if isinstance(a, (str, Path)) and not isinstance(b, (str, Path)):
            path, data = a, b
        else:
            data, path = a, b

    if path is None or data is None:
        raise TypeError("save(data, path) or save(path, data) or save(path)")

    p = _as_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    json_ready = _sets_to_lists(data)
    p.write_text(json.dumps(json_ready, indent=2))
    return p
