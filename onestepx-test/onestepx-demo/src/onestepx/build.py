from typing import Dict, Any, Iterable
from onestepx import collapse_to_terminal
from onestepx.cache import flags
from .reducers import available

def run_reducers(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    # allow multiple passes by materializing once
    data = list(records)
    out: Dict[str, Any] = {}
    for name, fn in available().items():
        res = fn(iter(data))
        # shallow merge of namespaces
        for k, v in res.items():
            if k in out and isinstance(out[k], dict) and isinstance(v, dict):
                out[k].update(v)
            else:
                out[k] = v
    return out

def build_and_attach(root_node, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    # collapse (O(1)) and stash reducer outputs on T
    collapse_to_terminal(root_node)
    flags().clear()
    flags().update(run_reducers(records))
    return flags()
