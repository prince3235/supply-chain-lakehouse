import shutil
import os
import time
from pathlib import Path

def quarantine_file(file_path, dataset, reason):
    ts = int(time.time())
    filename = os.path.basename(file_path)
    q_dir = Path(f"data/quarantine/{dataset}")
    q_dir.mkdir(parents=True, exist_ok=True)
    
    dest = q_dir / f"{ts}_{filename}"
    shutil.copy2(file_path, dest)
    
    with open(f"{dest}.reason", "w") as f:
        f.write(str(reason))
