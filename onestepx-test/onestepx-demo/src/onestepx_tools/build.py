
from typing import Dict, Any
from .ingest import load_rows
from .reducers import project_facets as project_bitsets  # alias OK
from .reducers import median_budget_by_status
from onestepx import TERMINAL

from onestepx import TERMINAL

# Ensure TERMINAL has a .flags dict (older onestepx may not attach it by default)
try:
    _ = TERMINAL.flags
except AttributeError:
    setattr(TERMINAL, "flags", {})
def build_and_attach(source_dir: str | None = None) -> Dict[str, Any]:
    rows = load_rows(source_dir or "./data")
    bits = project_bitsets(rows)                 # dict[str, set]
    med = median_budget_by_status(rows)          # dict[str, number]
    out = {
        "proj_bitsets": bits,
        "median_budget_by_status": med,
    }
    TERMINAL.flags.update(out)
    return out