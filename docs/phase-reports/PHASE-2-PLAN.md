# Phase 2 — AWS S3 Data Lake Foundation Plan

## 1. Objective
Build a secure, well-structured, cost-aware, Terraform-managed AWS S3 Data Lake foundation to store raw and curated data for the Supply Chain Lakehouse.

## 2. Current Infrastructure State
Phase 1 has established the Terraform structure (`environments/dev`), AWS provider configuration, initial Budget module, and IAM foundation with least privilege.

## 3. S3 Architecture
One dedicated S3 bucket in the `dev` environment acting as the data lake, containing documented logical prefixes (zones) representing the data lifecycle.

## 4. Bucket Strategy
The bucket name must be globally unique. We will use the format: `${var.project_name}-lake-${var.environment}-${data.aws_caller_identity.current.account_id}` to guarantee uniqueness while remaining readable.

## 5. Environment Strategy
Only the `dev` environment will be provisioned.

## 6. Data-Zone Strategy
Logical prefixes established:
- `landing/`: Temporary source landing area.
- `raw/`: Original source representation.
- `bronze/`: Future raw Lakehouse tables.
- `silver/`: Future cleaned and validated datasets.
- `gold/`: Future business-ready datasets.
- `features/`: Future ML feature datasets.
- `quarantine/`: Invalid/rejected data.
- `checkpoints/`: Future pipeline checkpoint metadata.
- `artifacts/`: Future data/ML artifacts.
*Note: S3 does not require physical folders. We will define these conceptually without creating empty objects, except where explicitly needed by Terraform to enforce structure if requested.*

## 7. Security Strategy
- Block Public Access completely (`aws_s3_bucket_public_access_block`).
- Enforce Object Ownership (`BucketOwnerEnforced`).
- Enforce secure transport (HTTPS only) via Bucket Policy.

## 8. Encryption Strategy
Enable default server-side encryption using Amazon S3 managed keys (`SSE-S3`). This is the most cost-effective and secure default for a dev environment without the overhead of KMS.

## 9. Versioning Strategy
Enable bucket versioning to protect against accidental overwrite or deletion of data.

## 10. Lifecycle Strategy
To minimize costs in the `dev` environment:
- Abort incomplete multipart uploads after 7 days.
- Retain noncurrent object versions for 30 days before expiring them.

## 11. Naming Strategy
Resources will follow the `supply-chain-lake-<env>` convention.

## 12. Tagging Strategy
Inherit `default_tags` defined in Phase 1 (Project, Environment, ManagedBy, Owner, CostCenter).

## 13. Terraform Implementation Plan
1. Create `infrastructure/terraform/modules/data-lake`.
2. Add `main.tf`, `variables.tf`, `outputs.tf` for the data lake module.
3. Integrate the `data-lake` module into `infrastructure/terraform/environments/dev/main.tf`.

## 14. Validation Plan
- `terraform fmt -check -recursive`
- `terraform init`
- `terraform validate`
- `terraform plan` (May be BLOCKED if AWS credentials are not yet available).

## 15. Cost Considerations
- Uses `SSE-S3` instead of `KMS` to save cost.
- Restricts noncurrent version retention to 30 days.
- No replication or advanced storage classes.

## 16. Disaster/Recovery Considerations
- Versioning is the primary defense mechanism against accidental deletions.

## 17. Explicit Non-Goals
- No Databricks integration.
- No Data processing pipelines (Bronze/Silver/Gold).
- No KMS keys.

## 18. Phase 2 Definition of Done
Terraform code is fully implemented, formatted, and validated. A plan is successfully generated and checked for unexpected resources. Code is clean and secure.
