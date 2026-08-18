# Phase 1: AWS Cloud Foundation Implementation Plan

## Current Repository State
- Phase 0 is completed (architecture documentation, specifications, data contracts, and implementation roadmap).
- The `infrastructure/terraform` and `infrastructure/databricks` directories are created but currently contain only `.gitkeep`.
- There is no existing Terraform configuration or AWS infrastructure code inside `infrastructure/terraform`.
- No `.gitignore` is found in the project root.

## Required Changes
1. **.gitignore**: Create a robust `.gitignore` for Terraform, AWS credentials, environment variables, etc.
2. **Terraform Structure**: Establish the base Terraform directory structure following best practices.
3. **AWS Provider**: Configure the AWS provider in a scalable, environment-aware manner without hardcoded credentials.
4. **IAM Configuration**: Define a base set of secure IAM roles (Developer, Infrastructure, S3 Access, Databricks Integration) adhering to least privilege.
5. **Cost Protection (Budgets)**: Set up AWS Budgets to alert on spending thresholds.
6. **Tagging Standard**: Implement a project-wide tagging convention via `default_tags` in the AWS provider.
7. **Documentation**: Create `infrastructure/terraform/README.md` and `docs/phase-reports/PHASE-1-IMPLEMENTATION.md`.

## AWS Resources Required
- AWS Budgets (monthly limit with alerts at 50%, 75%, 90%, 100%)
- AWS IAM Roles (e.g., `supply-chain-lake-dev-developer-role`, `supply-chain-lake-dev-infra-role`, `supply-chain-lake-dev-s3-access-role`, `supply-chain-lake-dev-databricks-role`)
- AWS IAM Policies to enforce least privilege for these roles.

## Terraform Structure
```
infrastructure/
└── terraform/
    ├── environments/
    │   └── dev/
    │       ├── main.tf
    │       ├── variables.tf
    │       ├── outputs.tf
    │       ├── providers.tf
    │       ├── terraform.tfvars.example
    │       └── versions.tf
    ├── modules/
    │   ├── budget/
    │   └── iam/
    └── README.md
```

## Security Considerations
- Ensure NO AWS credentials or secrets are committed.
- Secure `.gitignore` to explicitly exclude `*.tfstate`, `*.tfvars`, `.terraform/`, and `credentials`.
- Do not create S3 buckets or public resources in Phase 1.
- IAM roles must follow least privilege principle.

## Cost Considerations
- Phase 1 strictly provisions Budgets and IAM Roles, which are mostly free (IAM) or minimal cost (Budgets).
- No compute, storage, or external services are launched.
- Developer environment (dev) will have strict limits.

## Validation Strategy
- `terraform fmt -check`
- `terraform validate`
- `terraform plan`
- Review the generated plan to verify NO unexpected resources are created.
- Review Git status before commit to verify no secrets/state files.

## Expected Deliverables
- `.gitignore`
- `infrastructure/terraform/environments/dev/` configuration files
- `infrastructure/terraform/modules/budget/` and `iam/`
- `infrastructure/terraform/README.md`
- `docs/phase-reports/PHASE-1-IMPLEMENTATION.md`
- `docs/phase-reports/PHASE-1-COMPLETION.md`

## Explicit Non-Goals
- DO NOT implement S3 data lake, Bronze/Silver/Gold layers, or Databricks workspace.
- DO NOT create any ML pipelines, data ingestion, or Databricks compute resources.
