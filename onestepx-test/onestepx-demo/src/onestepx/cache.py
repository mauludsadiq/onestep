import json
from typing import Any, Dict
from onestepx import TERMINAL

def flags() -> Dict[str, Any]:
    if not hasattr(TERMINAL, "flags"):
        TERMINAL.flags = {}
    return TERMINAL.flags

def load(path: str = "onestepx_cache.json") -> Dict[str, Any]:
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    TERMINAL.flags = data
    return data

def save(path: str = "onestepx_cache.json") -> str:
    with open(path, "w") as f:
        json.dump(flags(), f)
    return path
