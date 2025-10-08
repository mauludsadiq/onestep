import numpy as np
from numba import njit, prange

# bitplanes: dict[str] -> np.ndarray(dtype=np.uint8) shape (N,)
# each entry is 0/1 per entity

@njit(parallel=True, fastmath=True)
def and_not(a, b, c):
    out = np.empty_like(a)
    for i in prange(a.size):
        out[i] = a[i] & b[i] & (1 ^ c[i])
    return out

@njit(parallel=True, fastmath=True)
def k_and(arrs):  # arrs: list of arrays
    out = arrs[0].copy()
    for k in range(1, len(arrs)):
        a = arrs[k]
        for i in prange(out.size):
            out[i] = out[i] & a[i]
    return out

@njit(parallel=True, fastmath=True)
def k_or(arrs):
    out = arrs[0].copy()
    for k in range(1, len(arrs)):
        a = arrs[k]
        for i in prange(out.size):
            out[i] = out[i] | a[i]
    return out

@njit(parallel=True, fastmath=True)
def popcount_u8(x):  # x: uint8 0/1 vector
    return x.sum()

def to_u8(ids, N):
    a = np.zeros(N, dtype=np.uint8)
    if isinstance(ids, (set, frozenset)):
        for i in ids:
            if 0 <= i < N:
                a[i] = 1
    else:
        a[np.asarray(list(ids), dtype=np.int64)] = 1
    return a

def build_bitplanes_from_sets(bitset_map, N):
    # bitset_map: dict[str, set[int]]
    return {k: to_u8(v, N) for k, v in bitset_map.items()}

def warmup(bp):
    # JIT compile once
    _ = and_not(bp["team_remote"], bp["status_delayed"], bp["deps_gt_10"])
    _ = k_and([bp["team_remote"], bp["status_delayed"]])
    _ = k_or([bp["team_remote"], bp["status_delayed"]])
    _ = popcount_u8(bp["team_remote"])
