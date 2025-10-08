import json, csv, pathlib

def load_rows(data_dir="./data"):
    """Load rows from JSON, JSONL, or CSV for test fixtures."""
    d = pathlib.Path(data_dir)
    rows = []
    if not d.exists():
        return []
    for p in d.rglob("*"):
        if p.suffix.lower() in (".jsonl", ".ndjson"):
            with p.open() as f:
                for line in f:
                    line=line.strip()
                    if line:
                        try:
                            rows.append(json.loads(line))
                        except Exception:
                            pass
        elif p.suffix.lower() == ".json":
            try:
                data = json.loads(p.read_text())
                if isinstance(data, list): rows.extend(data)
                elif isinstance(data, dict): rows.append(data)
            except Exception:
                pass
        elif p.suffix.lower() == ".csv":
            try:
                with p.open(newline="") as f:
                    rows.extend(csv.DictReader(f))
            except Exception:
                pass
    return rows
