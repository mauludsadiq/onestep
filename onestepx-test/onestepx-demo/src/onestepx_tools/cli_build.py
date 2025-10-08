import argparse, sys
from .ingest import ingest_path
from .build import build_and_attach
from .cache import save

def main(argv=None):
    ap = argparse.ArgumentParser("onestepx build")
    ap.add_argument("--source", required=True, help="Path containing JSON/YAML/CSV data")
    ap.add_argument("--out", default="onestepx_cache.json", help="Output cache file")
    args = ap.parse_args(argv)
    flags = build_and_attach(ingest_path(args.source))
    path = save(args.out)
    print(f"Built T-cache with keys: {list(flags.keys())}")
    print(f"Wrote: {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
