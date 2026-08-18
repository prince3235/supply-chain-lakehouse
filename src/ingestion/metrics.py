import json
import time
from pathlib import Path

class Metrics:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.total_files = 0
        self.valid_files = 0
        self.invalid_files = 0
        self.uploaded_files = 0
        self.skipped_files = 0
        self.failed_files = 0
        self.quarantined_files = 0
        self.total_rows = 0
        self.total_bytes = 0
        self.start_time = time.time()
        
    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "total_files": self.total_files,
            "valid_files": self.valid_files,
            "invalid_files": self.invalid_files,
            "uploaded_files": self.uploaded_files,
            "skipped_files": self.skipped_files,
            "failed_files": self.failed_files,
            "quarantined_files": self.quarantined_files,
            "total_rows": self.total_rows,
            "total_bytes": self.total_bytes,
            "duration_seconds": time.time() - self.start_time
        }
        
    def save(self):
        Path("reports").mkdir(exist_ok=True)
        with open("reports/ingestion_metrics.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)
