import json
import time
from pathlib import Path

class Manifest:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.entries = []
        Path("manifests/ingestion").mkdir(parents=True, exist_ok=True)
        
    def add_entry(self, dataset, source, dest, checksum, status, rows, size, error=None):
        self.entries.append({
            "batch_id": self.batch_id,
            "timestamp": time.time(),
            "dataset": dataset,
            "source_file": source,
            "destination": dest,
            "checksum": checksum,
            "status": status,
            "row_count": rows,
            "file_size": size,
            "error_reason": str(error) if error else None
        })
        
    def save(self):
        with open(f"manifests/ingestion/{self.batch_id}.json", "w") as f:
            json.dump(self.entries, f, indent=2)
