# Phase 4 — Data Ingestion Pipeline Plan

## 1. Objective
Build a production-oriented batch ingestion framework that discovers generated datasets from Phase 3, validates their configurations, schemas, and data contracts, and uploads them to the AWS S3 Lakehouse Foundation using idempotent, secure, and observable processes.

## 2. Ingestion Architecture
The pipeline follows a sequential, decoupled architecture:
1. Discovery (scan `data/generated/clean/` for `.parquet` or `.csv`)
2. Configuration & Registry Validation
3. Schema & Data Contract Validation
4. Data Quality Checks (Lightweight)
5. Idempotency Check (via local/S3 manifests or tags)
6. S3 Upload (to `raw/` prefix with partitioning)
7. Verification (checksum comparison)
8. Manifest & Audit Generation

## 3. Source Discovery
Scans the configured local directory (`data/generated/clean/` by default). Matches discovered files against the dataset registry. Warns on missing optional datasets, fails on missing required datasets (if any).

## 4. Supported Formats
- Parquet (Primary)
- CSV (Fallback/Secondary)

## 5. Dataset Registry
Located at `configs/datasets.yaml`. It defines expectations for all 10 datasets (sales, products, inventory, stores, warehouses, suppliers, shipments, returns, weather, calendar).

## 6. Schema Validation
Validates column presence, count, and data types before processing using PyArrow or Pandas metadata inspection.

## 7. Data Contract Validation
Enforces rules defined in `DATA_CONTRACT.md` (e.g., required columns, PK uniqueness). Handled during the quality validation step.

## 8. Data Quality Validation
Lightweight checks:
- No empty files
- Primary key presence
- No corrupt file structures
Invalid datasets route to a `quarantine/` directory.

## 9. S3 Destination Strategy
Target: Phase 2 S3 bucket under the `raw/` prefix. No writes to bronze/silver/gold.

## 10. Partitioning Strategy
- Master data (products, stores, warehouses, suppliers, calendar): `raw/<dataset>/snapshot_date=YYYY-MM-DD/`
- Transactional/Time-series (sales, inventory, shipments, returns, weather): `raw/<dataset>/year=YYYY/month=MM/day=DD/`

## 11. Idempotency Strategy
A local manifest/database tracks previously uploaded files by their SHA-256 checksum and source path. If an exact match is found, ingestion is skipped. Optionally, S3 object tagging or metadata can be checked.

## 12. Incremental Ingestion Strategy
Supports processing only new files since the last run. Handled automatically via the Idempotency strategy.

## 13. Retry Strategy
Transient AWS/Network errors are retried using exponential backoff (e.g., up to 3 times). Validation errors are never retried.

## 14. Quarantine Strategy
Files failing validation are moved to `data/quarantine/<dataset>/<timestamp>_<filename>` alongside an error report.

## 15. Manifest Strategy
A JSON manifest is written locally to `manifests/ingestion/` per run containing batch_id, file statuses, checksums, and row counts.

## 16. Audit Strategy
Audit logs capture detailed execution history, tracking success/failure states per dataset for governance.

## 17. Logging Strategy
Structured JSON or formatted text logging (info/error/warning) with contextual `batch_id`.

## 18. Metrics Strategy
Run-level metrics (total files, bytes uploaded, rows, duration) output to `reports/ingestion_metrics.json`.

## 19. Security
- AWS credentials sourced via IAM roles or `boto3` default chain.
- No hardcoded secrets.
- S3 transit over HTTPS.
- Least-privilege preserved.

## 20. Cost Controls
- Prevent duplicate uploads via idempotency.
- Avoid full in-memory loads of huge files (use metadata where possible).
- No new compute clusters (pure Python).

## 21. Testing
Unit tests using `pytest` and `moto` for S3 mocking. Includes:
- Validation logic
- Idempotency checks
- Quarantine routing
- Config loading

## 22. Failure Scenarios
- Missing source -> Log Warning or Error based on registry.
- Bad Schema -> Quarantine & Mark Failed.
- AWS Error -> Retry -> Fail Batch if persistent.
- Partial Failure -> Report accurately (e.g., 8 success, 2 fail).

## 23. Explicit Non-Goals
- No data transformations.
- No Databricks/Spark.
- No Bronze/Silver/Gold table creation.
- No ML training.

## 24. Definition of Done
As defined in the project specification, ensuring a fully functional, idempotent, tested ingestion pipeline to S3 `raw/` prefix.
