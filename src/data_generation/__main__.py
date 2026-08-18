import argparse
import os
import json
from pathlib import Path

from .config_loader import load_config
from .generators.master_data import generate_all_master_data
from .generators.transactional_data import generate_transactional_data
from .quality_injector import inject_quality_issues
from .validator import run_quality_gate

def save_datasets(datasets, base_dir, fmt="parquet"):
    os.makedirs(base_dir, exist_ok=True)
    for name, df in datasets.items():
        if df is None or df.empty:
            continue
            
        dataset_dir = os.path.join(base_dir, name)
        os.makedirs(dataset_dir, exist_ok=True)
        
        file_path = os.path.join(dataset_dir, f"data.{fmt}")
        if fmt == "parquet":
            df.to_parquet(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
            
def generate_manifest(datasets, output_dir, profile_name, mode):
    manifest = []
    for name, df in datasets.items():
        if df is None or df.empty: continue
        manifest.append({
            'dataset_name': name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'quality_mode': mode,
            'profile': profile_name
        })
    
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Supply Chain Synthetic Data Generator")
    parser.add_argument("--profile", type=str, default="small", help="Data volume profile (small, medium, large)")
    args = parser.parse_args()
    
    print(f"Loading configuration for profile: {args.profile}")
    try:
        config = load_config(profile=args.profile)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
        
    print("Generating Master Data...")
    master_data = generate_all_master_data(config)
    
    print("Generating Transactional Data...")
    txn_data = generate_transactional_data(config, master_data)
    
    clean_datasets = {**master_data, **txn_data}
    
    print("Injecting Data Quality Issues for Dirty Dataset...")
    dirty_datasets = inject_quality_issues(clean_datasets, config)
    
    print("\nRunning Quality Gates...")
    clean_pass = run_quality_gate(clean_datasets, mode="clean")
    dirty_pass = run_quality_gate(dirty_datasets, mode="dirty")
    
    if not clean_pass:
        print("CRITICAL: Clean dataset failed quality gate. Aborting save.")
        return
        
    output_dir = config.get("output_dir", "data/generated")
    fmt = config.get("output_format", "parquet")
    
    clean_dir = os.path.join(output_dir, "clean")
    dirty_dir = os.path.join(output_dir, "dirty")
    
    print(f"\nSaving generated datasets to {output_dir} as {fmt}...")
    save_datasets(clean_datasets, clean_dir, fmt)
    save_datasets(dirty_datasets, dirty_dir, fmt)
    
    generate_manifest(clean_datasets, clean_dir, args.profile, "clean")
    generate_manifest(dirty_datasets, dirty_dir, args.profile, "dirty")
    
    print("\nData Generation Complete!")

if __name__ == "__main__":
    main()
