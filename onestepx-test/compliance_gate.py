from onestepx import TERMINAL, collapse_to_terminal
from onestepx.hierarchy import Node
import random, time

class File(Node):
    def __init__(self, name, license_tag="MIT"):
        super().__init__(name)
        self.license_tag = license_tag

class Dir(Node):
    pass

def build_repo(num_dirs=100, files_per_dir=200, gpl_ratio=0.02):
    root = Dir("repo")
    rng = random.Random(42)
    for d in range(num_dirs):
        folder = Dir(f"pkg_{d}")
        root.add_child(folder)
        for f in range(files_per_dir):
            lic = "GPL-3.0" if rng.random() < gpl_ratio else "MIT"
            folder.add_child(File(f"file_{d}_{f}.py", license_tag=lic))
    return root

def scan_for_gpl(node):
    stack = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, File) and cur.license_tag.startswith("GPL"):
            return True
        for ch in getattr(cur, "children", []):
            stack.append(ch)
    return False

def set_terminal_flag(k, v):
    if not hasattr(TERMINAL, "flags"):
        TERMINAL.flags = {}
    TERMINAL.flags[k] = v

def get_terminal_flag(k):
    return getattr(TERMINAL, "flags", {}).get(k, False)

def requires_legal_review():
    return get_terminal_flag("has_gpl")

if __name__ == "__main__":
    repo = build_repo()
    t0 = time.time()
    has_gpl = scan_for_gpl(repo)
    t1 = time.time()
    collapse_to_terminal(repo)
    set_terminal_flag("has_gpl", has_gpl)
    t2 = time.time()
    for _ in range(10000):
        requires_legal_review()
    t3 = time.time()
    print(f"Initial scan: {t1 - t0:.3f}s")
    print(f"Collapse: {t2 - t1:.3f}s")
    print(f"10k O(1) checks: {t3 - t2:.3f}s")
    print(f"TERMINAL.flags = {TERMINAL.flags}")
