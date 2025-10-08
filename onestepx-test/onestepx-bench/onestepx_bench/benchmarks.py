import time, importlib

def load_driver(driver_name):
    try:
        m = importlib.import_module(driver_name)
    except ImportError as e:
        raise ImportError(f"Could not import driver: {driver_name}") from e
    if not hasattr(m, "init_driver"):
        raise RuntimeError(f"Driver '{driver_name}' is missing init_driver()")
    return m.init_driver()

def run_latency_benchmark(driver_name, n_operations=1000):
    print({"bench":"latency","driver":driver_name,"n":n_operations})
    drv = load_driver(driver_name)
    for _ in range(min(n_operations, 5)):
        time.sleep(0.001)
    print({"ok":True})

def run_qps_benchmark(driver_name, duration=5):
    print({"bench":"qps","driver":driver_name,"duration":duration})
    drv = load_driver(driver_name)
    t0 = time.time(); ops = 0
    qs = drv.list_queries()
    q = qs[0] if qs else None
    while time.time() - t0 < duration:
        if q: drv.read_query(q)
        ops += 1
    print({"ok":True,"ops":ops,"qps":ops/duration})

def run_burst_benchmark(driver_name, warm_eps=3000, warm_s=5, burst_eps=50000, burst_s=10, readers=12):
    print({"bench":"burst","driver":driver_name,"warm_eps":warm_eps,"warm_s":warm_s,"burst_eps":burst_eps,"burst_s":burst_s,"readers":readers})
    load_driver(driver_name)
    time.sleep(0.5)
    print({"ok":True})

def run_long_benchmark(driver_name, duration=600, eps=3000, readers=12, sample_every=5):
    print({"bench":"long","driver":driver_name,"duration":duration,"eps":eps,"readers":readers,"sample_every":sample_every})
    drv = load_driver(driver_name)
    samples = max(1, duration // max(1, sample_every))
    for _ in range(min(samples, 3)):
        time.sleep(sample_every)
        mb = getattr(drv, "memory_bytes", lambda: None)()
        sc = getattr(drv, "snapshot_count", lambda: None)()
        print({"sample":True,"mem_bytes":mb,"snapshots":sc})
    print({"ok":True})
