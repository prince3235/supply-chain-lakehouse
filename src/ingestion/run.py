import argparse
import uuid
import os
from .config import load_config
from .registry import load_registry
from .discovery import discover_files
from .checksum import calculate_checksum
from .idempotency import IdempotencyTracker
from .contract_validator import validate_contract
from .quality_validator import validate_quality
from .quarantine import quarantine_file
from .manifest import Manifest
from .metrics import Metrics
from .audit import log_audit
from .s3_client import S3Client
from .uploader import upload

def run(args):
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    config = load_config(args.config)
    registry = load_registry()
    tracker = IdempotencyTracker()
    manifest = Manifest(batch_id)
    metrics = Metrics(batch_id)
    
    base_path = "data/generated/clean" if args.quality == "clean" else "data/generated/dirty"
    
    datasets = None
    if not args.all and args.dataset:
        datasets = args.dataset
        
    discovered = discover_files(base_path, datasets)
    
    # Check for requested datasets missing
    if datasets:
        for ds in datasets:
            if ds not in discovered or not discovered[ds]:
                log_audit(batch_id, ds, "discovery", "failed", reason="Dataset not found")
                
    s3 = S3Client(config["aws_region"]) if not args.dry_run else None
    
    for ds, files in discovered.items():
        if ds not in registry:
            continue
            
        ds_config = registry[ds]
        
        for file_path in files:
            metrics.total_files += 1
            file_size = os.path.getsize(file_path)
            checksum = calculate_checksum(file_path)
            
            # Idempotency check
            if tracker.is_ingested(ds, checksum):
                metrics.skipped_files += 1
                log_audit(batch_id, ds, "ingestion", "skipped", reason="Already ingested", file=file_path)
                manifest.add_entry(ds, file_path, None, checksum, "SKIPPED", 0, file_size)
                continue
                
            try:
                # Validation
                rows = validate_contract(file_path, ds_config)
                validate_quality(file_path, ds_config)
                metrics.valid_files += 1
                
                # Upload
                if not args.dry_run:
                    dest = upload(s3, file_path, config["bucket_name"], ds_config, checksum, batch_id)
                    tracker.mark_ingested(ds, checksum)
                    metrics.uploaded_files += 1
                    metrics.total_rows += rows
                    metrics.total_bytes += file_size
                    log_audit(batch_id, ds, "upload", "success", file=file_path, dest=dest)
                    manifest.add_entry(ds, file_path, dest, checksum, "UPLOADED", rows, file_size)
                else:
                    log_audit(batch_id, ds, "dry_run_upload", "success", file=file_path)
                    manifest.add_entry(ds, file_path, "DRY_RUN", checksum, "DRY_RUN", rows, file_size)
                    
            except Exception as e:
                metrics.invalid_files += 1
                metrics.quarantined_files += 1
                log_audit(batch_id, ds, "validation", "quarantined", file=file_path, error=str(e))
                if not args.dry_run:
                    quarantine_file(file_path, ds, e)
                manifest.add_entry(ds, file_path, None, checksum, "QUARANTINED", 0, file_size, error=e)

    metrics.save()
    manifest.save()
    
    print(f"Total: {metrics.total_files}")
    print(f"Success: {metrics.uploaded_files}")
    print(f"Quarantine: {metrics.quarantined_files}")
    print(f"Skipped: {metrics.skipped_files}")
    
    if metrics.quarantined_files > 0:
        exit(1)
    exit(0)

if __name__ == "__main__":
    pass
