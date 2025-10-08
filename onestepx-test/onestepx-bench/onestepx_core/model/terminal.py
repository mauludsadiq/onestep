from __future__ import annotations
from typing import Dict, Set
from dataclasses import dataclass

Flag = str

@dataclass
class Terminal:
    flags: Dict[Flag, Set[str]]
    summaries: Dict[str, Dict[str, int]]
    version: int
