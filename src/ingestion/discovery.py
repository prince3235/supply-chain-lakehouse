import os
import glob

def discover_files(base_path, datasets=None):
    files = {}
    for ds in os.listdir(base_path):
        if datasets and ds not in datasets:
            continue
        ds_path = os.path.join(base_path, ds)
        if os.path.isdir(ds_path):
            files[ds] = glob.glob(f"{ds_path}/*.parquet") + glob.glob(f"{ds_path}/*.csv")
    return files
