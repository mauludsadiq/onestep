import os, json, csv
from typing import Dict, Iterable, Any, List, Optional
try:
    import yaml  # optional
except Exception:
    yaml = None

def iter_files(base: str, exts: Optional[List[str]] = None) -> Iterable[str]:
    for root, _, files in os.walk(base):
        for fn in files:
            if not exts or any(fn.endswith(e) for e in exts):
                yield os.path.join(root, fn)

def read_json(path: str) -> Iterable[Dict[str, Any]]:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict): yield data
    elif isinstance(data, list): yield from data

def read_yaml(path: str) -> Iterable[Dict[str, Any]]:
    if yaml is None:
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict): yield data
    elif isinstance(data, list): yield from data

def read_csv(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            yield dict(row)

def _to_int(x):
    try:
        return int(x)
    except Exception:
        return None

def normalize(record: Dict[str, Any]) -> Dict[str, Any]:
    out = {
        "type": record.get("type") or record.get("_type") or "unknown",
        "id": record.get("id") or record.get("_id") or record.get("name"),
        "budget": _to_int(record.get("budget")),
        "status": (record.get("status") or "").lower(),
        "team_loc": (record.get("team") or {}).get("location") or record.get("team_loc"),
        "deps": _to_int(record.get("dependencies") or record.get("deps")),
        "last_week_changes": _to_int(record.get("audit_last_week") or record.get("last_week_changes")),
        "skills": set(record.get("skills") or []),
        "timestamp": record.get("ts") or record.get("timestamp"),
    }
    return out

def ingest_path(path: str) -> Iterable[Dict[str, Any]]:
    for p in iter_files(path, exts=[".json", ".yaml", ".yml", ".csv"]):
        if p.endswith(".json"):
            for rec in read_json(p): yield normalize(rec)
        elif p.endswith((".yaml",".yml")) and yaml is not None:
            for rec in read_yaml(p): yield normalize(rec)
        elif p.endswith(".csv"):
            for rec in read_csv(p): yield normalize(rec)


def load_rows(src):
    """
    Accepts either:
      - a single path (str/Path)
      - an iterable/generator of paths
    Returns a flat list[dict] aggregated from all JSON files found.
    """
    import os, json
    from typing import Iterable
    def iter_json(path):
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for fn in files:
                    if fn.endswith(".json"):
                        full = os.path.join(root, fn)
                        with open(full) as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, dict):
                                    yield row
                        elif isinstance(data, dict):
                            yield data
        elif os.path.isfile(path) and path.endswith(".json"):
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                for row in data:
                    if isinstance(row, dict):
                        yield row
            elif isinstance(data, dict):
                yield data

    rows = []
    # Single path?
    if isinstance(src, (str, bytes, os.PathLike)):
        for r in iter_json(src):
            rows.append(r)
        return rows

    # Iterable/generator of paths
    try:
        for item in src:
            for r in iter_json(str(item)):
                rows.append(r)
        return rows
    except TypeError:
        # Not iterable – treat as single path fallback
        for r in iter_json(str(src)):
            rows.append(r)
        return rows

