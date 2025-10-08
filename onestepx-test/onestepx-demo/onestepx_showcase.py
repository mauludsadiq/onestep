import time, random, statistics, datetime as dt
from collections import defaultdict
from onestepx import TERMINAL, collapse_to_terminal
from onestepx.hierarchy import Node

# ---------- domain scaffolding (synthetic but large-ish) ----------
rng = random.Random(7)

class Project(Node):
    def __init__(self, pid, budget, status, team_loc, deps, last_week_changes, skills):
        super().__init__(f"Project-{pid}")
        self.pid = pid
        self.budget = budget
        self.status = status
        self.team_loc = team_loc
        self.deps = deps
        self.last_week_changes = last_week_changes
        self.skills = skills

class Employee(Node):
    def __init__(self, eid, manager_div, has_critical, cert_days_to_expire, workload_hours, pto_next_month):
        super().__init__(f"Emp-{eid}")
        self.eid = eid
        self.manager_div = manager_div
        self.has_critical = has_critical
        self.cert_days_to_expire = cert_days_to_expire
        self.workload_hours = workload_hours
        self.pto_next_month = pto_next_month

class ResourceAlloc(Node):
    def __init__(self, rid, cost, ts):
        super().__init__(f"Res-{rid}")
        self.rid = rid
        self.cost = cost
        self.ts = ts  # datetime

# Build a mixed hierarchy (we won’t traverse it after collapse; this is to simulate precompute)
root = Node("Enterprise")
projects = []
employees = []
allocs = []

N_PROJ = 20000
N_EMP  = 15000
N_ALLOC = 50000

for i in range(N_PROJ):
    budget = rng.randrange(1_000_000, 10_000_000)
    status = rng.choice(["ok","delayed","critical"])
    team_loc = rng.choice(["onsite","remote","hybrid"])
    deps = rng.randrange(0, 30)
    last_week_changes = rng.randrange(0, 12)
    skills = set(rng.sample(["ML","FE","BE","Cloud","Security"], rng.randrange(1,4)))
    p = Project(i, budget, status, team_loc, deps, last_week_changes, skills)
    projects.append(p)
    root.add_child(p)

for e in range(N_EMP):
    manager_div = rng.choice(["Engineering","Sales","G&A","Design"])
    has_critical = rng.random() < 0.2
    cert_days_to_expire = rng.randrange(0, 365)
    workload_hours = rng.randrange(20, 60)
    pto_next_month = rng.random() < 0.15
    emp = Employee(e, manager_div, has_critical, cert_days_to_expire, workload_hours, pto_next_month)
    employees.append(emp)
    root.add_child(emp)

base = dt.datetime(2024,1,1)
for r in range(N_ALLOC):
    cost = rng.randrange(100, 50_000)
    ts = base + dt.timedelta(days=rng.randrange(0, 700))
    ra = ResourceAlloc(r, cost, ts)
    allocs.append(ra)
    root.add_child(ra)

# Inject some cycles info (precomputed by your graph engine; we just simulate presence)
cycle_node_ratio = 0.03
cycle_node_ids = set(rng.sample(range(N_PROJ), int(N_PROJ*cycle_node_ratio)))

# ---------- PRECOMPUTE / REDUCERS (expensive ONCE) ----------
t0 = time.time()

# Faceted bitsets (as Python sets here) for project predicates
P_budget_gt_5m = {p.pid for p in projects if p.budget > 5_000_000}
P_status_delayed = {p.pid for p in projects if p.status == "delayed"}
P_team_remote = {p.pid for p in projects if p.team_loc == "remote"}
P_has_skill_ML = {p.pid for p in projects if "ML" in p.skills}
P_deps_gt_10 = {p.pid for p in projects if p.deps > 10}
P_audit_last_week_gt_5 = {p.pid for p in projects if p.last_week_changes > 5}

# Employee facets
E_has_critical = {e.eid for e in employees if e.has_critical}
E_manager_div_eng = {e.eid for e in employees if e.manager_div == "Engineering"}
E_cert_exp_30d = {e.eid for e in employees if e.cert_days_to_expire <= 30}
E_workload_gt_40 = {e.eid for e in employees if e.workload_hours > 40}
E_on_pto_next_month = {e.eid for e in employees if e.pto_next_month}

# Recursive aggregation over resource allocations (time-filtered)
cutoff = dt.datetime(2024,1,1)
sum_cost_after = sum(a.cost for a in allocs if a.ts >= cutoff)

# Cycles summary (e.g., Tarjan/Johnson offline; here only presence + sample)
cycles_present = len(cycle_node_ids) > 0
sample_cycles = list(sorted(cycle_node_ids))[:10]

# Temporal admin changes / descendant impact (simulated precompute)
admin_last7d_affects_gt100 = rng.randrange(50, 250)  # pretend this is a computed count

# Anomaly detection on descendant rate-of-change (simulated)
anomaly_descendant_roc = True  # say we detected one

# Median metric grouped by ancestor field (simulate: per division workload median)
median_workload_by_div = defaultdict(list)
for e in employees:
    median_workload_by_div[e.manager_div].append(e.workload_hours)
median_workload_by_div = {k: statistics.median(v) for k,v in median_workload_by_div.items()}

# Shortest path “approvedBy” precomputed pairs (toy cache)
shortest_path_len = {("Emp-1","Emp-999"): 4, ("Emp-42","Emp-77"): 2}

t1 = time.time()

# ---------- COLLAPSE TO T ----------
T = collapse_to_terminal(root)  # singleton

# ---------- STASH ALL MATERIALIZED VIEWS ON T ----------
if not hasattr(TERMINAL, "flags"):
    TERMINAL.flags = {}

flags = TERMINAL.flags
flags["proj_bitsets"] = {
    "budget_gt_5m": P_budget_gt_5m,
    "status_delayed": P_status_delayed,
    "team_remote": P_team_remote,
    "has_skill_ML": P_has_skill_ML,
    "deps_gt_10": P_deps_gt_10,
    "audit_last_week_gt_5": P_audit_last_week_gt_5,
}
flags["emp_bitsets"] = {
    "has_critical": E_has_critical,
    "manager_div_eng": E_manager_div_eng,
    "cert_exp_30d": E_cert_exp_30d,
    "workload_gt_40": E_workload_gt_40,
    "on_pto_next_month": E_on_pto_next_month,
}
flags["sum_cost_after_2024_01_01"] = sum_cost_after
flags["cycles_present"] = cycles_present
flags["cycle_nodes_sample"] = sample_cycles
flags["admin_last7d_affects_gt100"] = admin_last7d_affects_gt100
flags["anomaly_descendant_rate_of_change"] = anomaly_descendant_roc
flags["median_workload_by_div"] = median_workload_by_div
flags["shortest_path_len"] = shortest_path_len

t2 = time.time()

# ---------- POST-COLLAPSE QUERIES (O(1) on T + set math) ----------
def q_projects_big_delayed_remote_ml_manydeps_recent():
    b = flags["proj_bitsets"]
    s = b["budget_gt_5m"] & b["status_delayed"] & b["team_remote"] & b["has_skill_ML"] & b["deps_gt_10"] & b["audit_last_week_gt_5"]
    return s

def q_employees_heavy_constraints():
    e = flags["emp_bitsets"]
    s = (e["has_critical"] & e["manager_div_eng"] & e["cert_exp_30d"] & e["workload_gt_40"]) - e["on_pto_next_month"]
    return s

def q_sum_all_costs_after_cutoff():
    return flags["sum_cost_after_2024_01_01"]

def q_cycles_present():
    return flags["cycles_present"], flags["cycle_nodes_sample"]

def q_temporal_admin_changes():
    return flags["admin_last7d_affects_gt100"] >= 100

def q_median_workload_by_div():
    return flags["median_workload_by_div"]

def q_shortest_path_len(a,b):
    return flags["shortest_path_len"].get((a,b), None)

# Execute queries and measure only the read time (no traversal)
r0 = time.time()
A = q_projects_big_delayed_remote_ml_manydeps_recent()
r1 = time.time()
B = q_employees_heavy_constraints()
r2 = time.time()
C = q_sum_all_costs_after_cutoff()
r3 = time.time()
D = q_cycles_present()
r4 = time.time()
E = q_temporal_admin_changes()
r5 = time.time()
F = q_median_workload_by_div()
r6 = time.time()
G = q_shortest_path_len("Emp-1","Emp-999")
r7 = time.time()

print("=== TIMINGS (seconds) ===")
print(f"precompute (reducers) : {t1 - t0:.3f}")
print(f"collapse_to_terminal  : {t2 - t1:.6f}")
print(f"Q1 projects facets    : {r1 - r0:.6f}  (answers: {len(A)})")
print(f"Q2 employees facets   : {r2 - r1:.6f}  (answers: {len(B)})")
print(f"Q3 sum costs          : {r3 - r2:.6f}  (value: {C})")
print(f"Q4 cycles present     : {r4 - r3:.6f}  (present: {D[0]}, sample: {D[1][:3]}...)")
print(f"Q5 temporal gate      : {r5 - r4:.6f}  (gate: {E})")
print(f"Q6 medians by division: {r6 - r5:.6f}  (keys: {list(F.keys())})")
print(f"Q7 shortest path len  : {r7 - r6:.6f}  (Emp-1 -> Emp-999: {G})")

print("\n=== NOTE ===")
print("All Q* ran on T (TERMINAL.flags) with set/index arithmetic — no hierarchy traversal.")
