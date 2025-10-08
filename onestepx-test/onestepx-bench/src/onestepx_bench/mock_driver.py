import time, random
class Driver:
    def __init__(self):
        self._queries = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7"]
        self.snapshots = 0
    def mutate_once(self): self.snapshots += 1
    def read_query(self,name): time.sleep(0.0005); return [f"id_{i}" for i in range(10)]
    def list_queries(self): return self._queries
    def snapshot_count(self): return self.snapshots
    def memory_bytes(self): return None
def init_driver(**kw): return Driver()
