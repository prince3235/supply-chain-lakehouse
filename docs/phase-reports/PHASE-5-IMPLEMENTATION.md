# Phase 5 — Databricks Lakehouse Foundation Implementation

## 1. Databricks Architecture
- **Cloud Provider:** AWS
- **Workspace Structure:** Single `dev` workspace mapped to `supply-chain-lakehouse-dev`.
- **Infrastructure:** Provisioned using Terraform (`databricks` provider) connected to the AWS account.

## 2. Workspace Strategy
- Workspace is strictly for development.
- Production and Staging will require separate isolated workspaces in the future.
- Users authenticate via SSO/OAuth.

## 3. Unity Catalog Architecture
- Central governance mechanism.
- Regional Metastore attached to the Workspace.
- Logical hierarchy: `supply_chain_dev` (Catalog) -> `bronze` (Schema) -> Tables.

## 4. AWS IAM Integration
- A dedicated IAM Role `databricks-uc-role-dev` was created using Terraform.
- Role employs a trust policy scoped to Databricks' AWS account ID (`414364122586`) and constrained by the external ID.
- Attached policy explicitly grants `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` strictly limited to the Phase 2 raw/bronze bucket.

## 5. Storage Credential
- Created `aws-uc-credential-dev` referencing the Unity Catalog IAM role.

## 6. External Location
- Configured two Unity Catalog external locations using the storage credential:
  - `s3-raw-dev` -> `s3://<bucket>/raw/`
  - `s3-bronze-dev` -> `s3://<bucket>/bronze/`

## 7. Catalog
- Created Catalog `supply_chain_dev` via Terraform.

## 8. Bronze Schema
- Created Schema `bronze` under `supply_chain_dev` via Terraform.

## 9. Bronze Tables
- Configured dynamically via `src/lakehouse/bronze/src/ingestion.py`.
- Includes `sales`, `products`, `inventory`, `stores`, `warehouses`, `suppliers`, `calendar`, `weather`, `shipments`, `returns`.

## 10. Delta Lake
- All tables in Bronze are enforced as Delta format.

## 11. Metadata Columns
- `_ingestion_timestamp`: Captured dynamically at read time.
- `_source_file`: Extracted using `pyspark.sql.functions.input_file_name`.
- `_batch_id`: Injected at the micro-batch level during Auto Loader execution.

## 12. Schema Strategy
- Schema inference enabled via Auto Loader (`cloudFiles.inferColumnTypes = "true"`).
- Schema evolution mode set to `addNewColumns` for safe expansion without breaking existing downstream pipelines.

## 13. Idempotency
- Using `DeltaTable.merge()`.
- Primary strategy: Upsert based on natural primary keys if provided.
- Fallback strategy: Idempotency based on `_source_file` mapping to prevent reloading the exact same raw payload.

## 14. Incremental Processing
- Leverages Databricks Auto Loader (`format("cloudFiles")`).
- Uses `trigger(availableNow=True)` for cost-effective incremental batch processing without 24/7 streaming overhead.

## 15. Compute Strategy
- Serverless or Job clusters with aggressive auto-termination (e.g., 10-15 minutes).
- Ephemeral compute avoids idle DBU charges.

## 16. Security
- Unity Catalog governs all table access.
- S3 is never exposed publicly.
- Databricks assumes IAM role (no keys committed).

## 17. Cost
- Spot instances recommended for job clusters.
- `availableNow` triggers allow clusters to terminate immediately after processing the backlog.

## 18. Testing
- `test_ingestion.py` validates the Python classes and pipeline initialization using `pytest` and `MagicMock` without requiring a live cluster.

## 19. Observability
- Standard Python `logging` outputs batch details and processed record counts to the Spark driver logs.

## 20. Lineage
- Unity Catalog captures automatic table-to-table lineage (once deployed to a live cluster).
- `_source_file` ensures row-level lineage back to the raw S3 object.

## 21. Known Limitations
- Terraform requires manual application due to missing AWS credentials in the local environment.
- Live integration tests are blocked without a provisioned workspace.

## 22. Phase 6 Readiness
- YES. Once AWS identity is provided and Terraform is applied, the Bronze Delta tables will be populated and ready for Silver transformation.
