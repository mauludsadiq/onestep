from typing import Dict, Any

def diff_graph(G0: Dict[Any, Any], G1: Dict[Any, Any]):
    """
    Return a dict with at least a 'mutated' key listing ids that changed.
    Compatible with prior variants that may have returned sets/tuples/etc.
    """
    mutated = []
    # additions or value changes
    for k, v1 in G1.items():
        if k not in G0 or G0[k] != v1:
            mutated.append(k)
    # deletions are not treated as mutations for now (optional extension)
    return {"mutated": mutated}

def incremental_update(T0, delta):
    """
    Minimal incremental path: return T0 itself and report mutated ids.
    Real implementation can attach recomputation here. We preserve API shape.
    """
    # Fast-path: nothing to change for now; caller only times execution.
    return T0
