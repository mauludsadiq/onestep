import time, importlib, statistics, json, argparse

def run_driver(path):
    mod = importlib.import_module(path)
    return mod.init_driver()

def latency(drv,n):
    t=[]
    for _ in range(n):
        s=time.perf_counter(); drv.mutate_once(); t.append(time.perf_counter()-s)
    print(json.dumps({
        "mean":statistics.mean(t),
        "p50":statistics.quantiles(t,n=100)[49],
        "p90":statistics.quantiles(t,n=100)[89],
        "p99":statistics.quantiles(t,n=100)[98]
    },indent=2))

def qps(drv,dur):
    q=drv.list_queries(); s=time.perf_counter(); c=0
    while time.perf_counter()-s<dur:
        for name in q: drv.read_query(name); c+=1
    print(f"total={c}  qps≈{c/dur:.1f}")

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd")
    p_lat=sub.add_parser("latency"); p_lat.add_argument("--driver"); p_lat.add_argument("--n",type=int,default=10000)
    p_qps=sub.add_parser("qps"); p_qps.add_argument("--driver"); p_qps.add_argument("--duration",type=int,default=10)
    args=p.parse_args()
    drv=run_driver(args.driver)
    if args.cmd=="latency": latency(drv,args.n)
    elif args.cmd=="qps": qps(drv,args.duration)
    else: p.print_help()
if __name__=="__main__": main()
