from __future__ import annotations
from dataclasses import dataclass, asdict
import time, json, pathlib

@dataclass
class Day1Metrics:
    method: str
    t_us: int
    affected_flags: int
    affected_nodes: int
    total_flags: int
    total_nodes: int
    timestamp_ns: int

def emit(metrics: Day1Metrics, path="onestepx_core/benches/bench_day1.jsonl"):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    rec = asdict(metrics)
    rec["timestamp_ns"] = time.time_ns()
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
