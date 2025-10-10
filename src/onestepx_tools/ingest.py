
from __future__ import annotations
from pathlib import Path
import json, csv
from typing import Iterable, Dict, Any, List

def _iter_json_file(p: Path) -> Iterable[Dict[str, Any]]:
    data = json.loads(p.read_text())
    if isinstance(data, dict):
        # single object or {"rows":[...]}
        rows = data.get("rows", data)
        if isinstance(rows, dict):
            yield rows
        elif isinstance(rows, list):
            for r in rows:
                if isinstance(r, dict):
                    yield r
    elif isinstance(data, list):
        for r in data:
            if isinstance(r, dict):
                yield r

def _iter_jsonl_file(p: Path) -> Iterable[Dict[str, Any]]:
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    yield obj
            except Exception:
                continue

def _iter_csv_file(p: Path) -> Iterable[Dict[str, Any]]:
    with p.open(newline="") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            # Best-effort cast numerics
            out = {}
            for k, v in row.items():
                if v is None:
                    out[k] = v
                    continue
                s = str(v).strip()
                if s == "":
                    out[k] = None
                    continue
                try:
                    out[k] = int(s)
                    continue
                except Exception:
                    pass
                try:
                    out[k] = float(s)
                    continue
                except Exception:
                    pass
                out[k] = v
            yield out

def load_rows(path: str | Path) -> List[Dict[str, Any]]:
    """
    Load rows (list[dict]) from a directory containing data files.
    Supports: .json, .jsonl/.ndjson, .csv. Returns a flat list of dicts.
    """
    root = Path(path)
    if root.is_file():
        files = [root]
    else:
        files = sorted([*root.glob("*.json"), *root.glob("*.jsonl"), *root.glob("*.ndjson"), *root.glob("*.csv")])

    rows: List[Dict[str, Any]] = []
    for p in files:
        if p.suffix.lower() == ".csv":
            rows.extend(_iter_csv_file(p))
        elif p.suffix.lower() in {".jsonl", ".ndjson"}:
            rows.extend(_iter_jsonl_file(p))
        elif p.suffix.lower() == ".json":
            rows.extend(_iter_json_file(p))
    return rows
