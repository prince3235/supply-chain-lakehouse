# Phase 1 — AWS Cloud Foundation Implementation

## 1. What Was Implemented
- A secure project `.gitignore` explicitly excluding state files and secrets.
- Baseline Terraform directory structure emphasizing modularity (`environments/` vs `modules/`).
- Terraform `budget` module for setting cost controls and alerting on AWS spend.
- Terraform `iam` module defining four strict, least-privilege roles for development.
- Development environment configuration (`environments/dev`) integrating the modules.
- Instructions in `infrastructure/terraform/README.md` for developers.

## 2. Why Each Component Exists
- **.gitignore**: Prevents catastrophic security breaches (leaked credentials) and state corruption.
- **Budget Module**: Prevents unexpected cloud bills by alerting at thresholds (50%, 75%, 90%, 100%).
- **IAM Module**: Pre-establishes roles for future pipeline and developer access so we do not use root or AdministratorAccess.
- **Environments Directory**: Supports separating `dev`, `staging`, and `prod` easily in the future.

## 3. AWS Architecture
The architecture provisions:
- AWS Budgets (Cost Management)
- IAM Roles (Developer, Infrastructure, Databricks, S3 Access)
No underlying compute, databases, or S3 buckets were created as per Phase 1 scope constraints.

## 4. Terraform Structure
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

## 5. IAM Strategy
- **Developer Role**: Limited privileges explicitly for engineers.
- **Infrastructure Role**: For CI/CD or Terraform running the infrastructure.
- **S3 Access Role**: For isolated S3 bucket reads/writes.
- **Databricks Role**: For the Databricks cluster to access AWS securely.
Each role currently assumes the root AWS account ID, which must be executed via STS.

## 6. Budget Strategy
A monthly AWS budget is configured in the `dev` environment with an ultra-low threshold limit (e.g. $10) and alerts at 50%, 75%, 90%, and 100% of the limit to designated emails.

## 7. Tagging Strategy
Defined centrally in the AWS provider configuration in `environments/dev/providers.tf` using `default_tags`:
- `Project`: supply-chain-lakehouse
- `Environment`: dev
- `ManagedBy`: terraform
- `Owner`: data-engineering-team
- `CostCenter`: 100-supply-chain

## 8. Security Strategy
- Strict `.gitignore` enforcement.
- Terraform code review via `fmt` and `validate`.
- Least Privilege IAM roles.
- No public resources.

## 9. Credential Strategy
No credentials are hardcoded. Terraform relies on standard AWS credential resolution (AWS CLI profile, environment variables like `AWS_ACCESS_KEY_ID`, or EC2 instance profiles).

## 10. State Strategy
For Phase 1, state is strictly local but ignored by Git. In Phase 2, this will be migrated to an S3 backend with DynamoDB locking.

## 11. How to Initialize Terraform
`terraform init` in `infrastructure/terraform/environments/dev/`

## 12. How to Validate Terraform
`terraform fmt -check -recursive`
`terraform validate`

## 13. How to Create a Plan
`terraform plan` (requires AWS credentials in the environment).

## 14. How to Apply
`terraform apply`

## 15. How to Destroy Development Resources
`terraform destroy`

## 16. How to Verify AWS Resources
Once applied, log in to the AWS Console, navigate to AWS Budgets and IAM Roles, and verify existence and tags.

## 17. Known Limitations
- Current IAM roles use placeholders for assuming principals; they point to the root account ID but will need concrete trusted identities later (e.g. OIDC).
- State is local for now.

## 18. Future Improvements
- Migrate state to S3 backend.
- Integrate AWS SSO/Identity Center instead of pure IAM roles for developer access.
