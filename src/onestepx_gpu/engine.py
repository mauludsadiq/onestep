
import torch, time

def _popcount32(x: torch.Tensor) -> torch.Tensor:
    if x.dtype != torch.int32:
        x = x.to(torch.int32)
    lut = torch.arange(256, device=x.device, dtype=torch.int64)
    lut = (lut.unsqueeze(1) & torch.tensor([1,2,4,8,16,32,64,128], device=x.device, dtype=torch.int64)).ne(0).sum(1)

    n = x.numel()
    bytes_flat = x.view(torch.uint8).reshape(n * 4)              # reinterpret as bytes
    looked = lut.index_select(0, bytes_flat.long()).view(n, 4)   # lookup per byte
    counts = looked.sum(1).to(torch.int32)                       # sum 4 bytes per word
    return counts.view(x.shape)

def fused_and_popcount_3way_resident(A, B, C, batch, repeats=10):
    device = A.device
    total = 0
    t0 = time.perf_counter()
    for _ in range(repeats):
        A32 = A.view(torch.int32)
        B32 = B.view(torch.int32)
        C32 = C.view(torch.int32)
        X = torch.bitwise_and(torch.bitwise_and(A32, B32), torch.bitwise_not(C32))
        total += _popcount32(X).sum().item()
    elapsed = time.perf_counter() - t0
    return {
        "repeats": repeats,
        "total_last": total,
        "total_mean": total / repeats,
        "elapsed_s": elapsed,
        "throughput_ops_per_s": total / elapsed,
    }
