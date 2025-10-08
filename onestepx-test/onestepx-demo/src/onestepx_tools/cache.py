import json
from typing import Any, Dict
from onestepx import TERMINAL

def flags() -> Dict[str, Any]:
    if not hasattr(TERMINAL, "flags"):
        TERMINAL.flags = {}
    return TERMINAL.flags

def _encode(o):
    if isinstance(o, set):
        return sorted(o)
    if isinstance(o, dict):
        # recursively encode nested sets
        return {k: _encode(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_encode(x) for x in o]
    return o

def _postprocess(d: Dict[str, Any]) -> Dict[str, Any]:
    pb = d.get("proj_bitsets")
    if isinstance(pb, dict):
        for k, v in list(pb.items()):
            if isinstance(v, list):
                pb[k] = set(v)
    return d

def load(path: str = "onestepx_cache.json") -> Dict[str, Any]:
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    data = _postprocess(data)
    TERMINAL.flags = data
    return data

def save(path: str = "onestepx_cache.json") -> str:
    with open(path, "w") as f:
        json.dump(_encode(flags()), f)
    return path
