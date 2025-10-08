import argparse, sys
from onestepx.hierarchy import Node
from onestepx.ingest import ingest_path
from onestepx.build import build_and_attach
from onestepx.cache import save

def main(argv=None):
    ap = argparse.ArgumentParser("onestepx build")
    ap.add_argument("--source", required=True, help="Path containing JSON/YAML/CSV data")
    ap.add_argument("--out", default="onestepx_cache.json", help="Output cache file")
    args = ap.parse_args(argv)
    root = Node("Root")  # we don't traverse post-collapse
    recs = ingest_path(args.source)
    flags = build_and_attach(root, recs)
    path = save(args.out)
    print(f"Built T-cache with keys: {list(flags.keys())}")
    print(f"Wrote: {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
