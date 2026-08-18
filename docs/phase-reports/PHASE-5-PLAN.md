# Phase 5 — Databricks Lakehouse Foundation Plan

## 1. Objective
Establish the Databricks Workspace on AWS, configure Unity Catalog governance with secure S3 integration via IAM roles, and implement the Bronze Delta layer to ingest the raw Phase 4 data using idempotent, incremental PySpark pipelines.

## 2. Databricks Architecture
- **Cloud:** AWS
- **Workspace:** `supply-chain-lakehouse-dev`
- **Compute:** Serverless or small interactive clusters with auto-termination (15 mins) to minimize costs. No always-on compute.

## 3. AWS Integration & IAM Strategy
- **IAM Role:** `databricks-uc-access-role` with least privilege access to the specific S3 raw/ and bronze/ prefixes.
- **Trust Policy:** Configured to trust the Databricks AWS account for Unity Catalog.
- **Credentials:** No hardcoded AWS keys; Databricks assumes the IAM role.

## 4. Unity Catalog Architecture
- **Metastore:** AWS regional metastore assigned to the workspace.
- **Storage Credential:** Named `aws_uc_credential` mapped to the IAM role.
- **External Location:** `s3_raw` mapping to `s3://<bucket>/raw/` and `s3_bronze` mapping to `s3://<bucket>/bronze/`.
- **Catalog:** `supply_chain_dev`
- **Schema:** `bronze`

## 5. Bronze Delta Architecture
- **Purpose:** Source-aligned, minimally transformed landing zone.
- **Format:** Delta Lake.
- **Tables:** `sales`, `products`, `inventory`, `stores`, `warehouses`, `suppliers`, `calendar`, `weather`, `shipments`, `returns`.
- **Metadata Columns:** `_ingestion_timestamp`, `_source_file`, `_batch_id`.
- **Idempotency:** Merge logic based on `_source_file` or dataset-specific primary keys to prevent duplicates.
- **Incremental:** Auto Loader (`cloudFiles`) or structured streaming batch triggers from S3 `raw/` to Delta `bronze/`.

## 6. Infrastructure As Code
- The existing Terraform AWS setup will be extended in a separate `modules/databricks` module to manage workspace, catalog, external locations, and grants, avoiding overlap with core AWS networking.

## 7. Data Quality & Schema Strategy
- **Schema Validation:** Use `mergeSchema = "false"` initially, with manual evolution allowed via `schemaTracking`.
- **Data Quality:** Lightweight PySpark expectations or simple row rejection for corrupt files (rescued data column). No business logic validation at Bronze.

## 8. Deployment Strategy
- Logic developed as reusable Python modules in `src/lakehouse/bronze/`.
- Executed via Databricks Workflows (Jobs) using task orchestration.

## 9. Security & Cost Controls
- Unity Catalog permissions restricted via `GRANT` statements.
- Job clusters used instead of all-purpose clusters for scheduled runs.
- Spot instances favored for dev compute.

## 10. Explicit Non-Goals
- No Silver/Gold transformations.
- No Machine Learning / MLflow.
- No BI/Dashboards.
- No real-time Kafka streaming.

## 11. Definition of Done
- Databricks Terraform code written.
- Bronze PySpark ingestion module implemented with idempotency and schema validation.
- Unit tests written.
- Documentation created.
- (Live validation blocked due to missing AWS/Databricks credentials).
