from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Iterable, Union

try:
    # attach to the real onestepx TERMINAL so identity checks pass
    from onestepx import TERMINAL
except Exception:  # fallback dummy for edit-time
    class _T: ...
    TERMINAL = _T()
    setattr(TERMINAL, "flags", {})

JsonablePath = Union[str, Path]

def _lists_to_sets(obj: Any) -> Any:
    if isinstance(obj, list):
        return set(obj)
    if isinstance(obj, dict):
        return {k: _lists_to_sets(v) for k, v in obj.items()}
    return obj

def _sets_to_lists(obj: Any) -> Any:
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, dict):
        return {k: _sets_to_lists(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sets_to_lists(v) for v in obj]
    return obj

def load(path: JsonablePath) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        # ensure TERMINAL.flags exists and is an empty dict object
        TERMINAL.flags = {}
        return TERMINAL.flags
    with p.open() as f:
        raw = json.load(f)
    fixed = _lists_to_sets(raw)
    # IMPORTANT: satisfy "TERMINAL.flags is flags" identity checks
    TERMINAL.flags = fixed
    return TERMINAL.flags

def save(*args, **kwargs) -> Path:
    """
    Supported forms:
      - save(data, path)
      - save(path, data)
      - save(path)              -> saves current TERMINAL.flags
      - save(path=..., data=...) or save(data=..., path=...)
    """
    data = kwargs.get("data")
    path = kwargs.get("path")

    if len(args) == 2 and (data is None or path is None):
        a, b = args
        if isinstance(a, (str, Path)) and not isinstance(b, (str, Path)):
            path, data = a, b
        elif isinstance(b, (str, Path)) and not isinstance(a, (str, Path)):
            data, path = a, b
        else:
            # ambiguous but keep behavior: treat as (data, path)
            data, path = a, b
    elif len(args) == 1 and (data is None or path is None):
        # save(path) -> take data from TERMINAL.flags
        single = args[0]
        if isinstance(single, (str, Path)):
            path = single
            data = data if data is not None else getattr(TERMINAL, "flags", {})
        else:
            # save(data) -> need a path kwarg
            data = single
            if path is None:
                raise TypeError("save(data, path) requires a path")
    elif len(args) > 2:
        raise TypeError("save() expects at most two positional arguments")

    if path is None or data is None:
        raise TypeError("save(data, path) or save(path, data) or save(path)")

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    json_ready = _sets_to_lists(data)
    with p.open("w") as f:
        json.dump(json_ready, f, indent=2)
    return p
