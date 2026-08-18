import json
import os
from pathlib import Path

IDEMPOTENCY_FILE = "manifests/idempotency.json"

class IdempotencyTracker:
    def __init__(self):
        self.record = {}
        Path("manifests").mkdir(exist_ok=True)
        if os.path.exists(IDEMPOTENCY_FILE):
            with open(IDEMPOTENCY_FILE, "r") as f:
                self.record = json.load(f)
                
    def is_ingested(self, dataset, checksum):
        return checksum in self.record.get(dataset, [])
        
    def mark_ingested(self, dataset, checksum):
        if dataset not in self.record:
            self.record[dataset] = []
        self.record[dataset].append(checksum)
        with open(IDEMPOTENCY_FILE, "w") as f:
            json.dump(self.record, f)
