
try:
    import cupy as cp
except Exception:  # allow import-time probe from other modules
    cp = None

class GPUFlags:
    """
    Keep boolean masks resident on GPU and do fast k-way intersections.
    Construct from Python sets of ints (e.g., TERMINAL.flags["proj_bitsets"][...]).
    """
    def __init__(self, size:int):
        if cp is None:
            raise RuntimeError("CuPy not available")
        self.size = int(size)
        self.masks = {}  # name -> cp.ndarray(bool)

    def add_mask(self, name:str, indices:set[int]):
        m = cp.zeros(self.size, dtype=cp.bool_)
        if indices:
            idx = cp.asarray(list(indices), dtype=cp.int32)
            m[idx] = True
        self.masks[name] = m

    def intersect(self, names:list[str]):
        if not names: 
            return cp.zeros(self.size, dtype=cp.bool_)
        out = self.masks[names[0]]
        for n in names[1:]:
            out = out & self.masks[n]
        return out

def build_gpu_from_terminal(term_flags:dict, keys:list[str]):
    """
    term_flags = TERMINAL.flags["proj_bitsets"] (dict[str] -> set[int] or list[int])
    keys = which flags to load
    """
    if cp is None:
        raise RuntimeError("CuPy not available")
    # discover max id to size the mask
    mx = 0
    for k in keys:
        s = term_flags.get(k, set())
        if not isinstance(s, set): s = set(s)
        if s:
            mx = max(mx, max(s))
    size = mx + 1
    gf = GPUFlags(size)
    for k in keys:
        s = term_flags.get(k, set())
        if not isinstance(s, set): s = set(s)
        gf.add_mask(k, s)
    return gf
