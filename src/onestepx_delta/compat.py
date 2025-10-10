from typing import Any, Dict, Iterable, Set

def normalize_delta(d: Any) -> Dict[str, Set]:
    """
    Accepts several shapes:
      {"mutated": [...]}
      {"added_nodes": [...], "removed_nodes": [...], "changed_nodes": [...]}
      set([...])  # legacy
    Returns {"mutated": set(...)}.
    """
    def as_set(x: Iterable) -> Set: return set(x or [])
    # Already normalized
    if isinstance(d, dict) and "mutated" in d:
        return {"mutated": as_set(d["mutated"])}
    # Multi-key form
    if isinstance(d, dict):
        muts = as_set(d.get("mutated")) | as_set(d.get("added_nodes")) | as_set(d.get("removed_nodes")) | as_set(d.get("changed_nodes"))
        return {"mutated": muts}
    # Bare set/list
    if isinstance(d, (set, list, tuple)):
        return {"mutated": set(d)}
    # Fallback
    return {"mutated": set()}
