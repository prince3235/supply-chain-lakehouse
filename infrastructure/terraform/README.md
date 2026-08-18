# Supply Chain Lakehouse — Terraform Infrastructure

This directory contains the Terraform configuration for the Supply Chain Lakehouse.

## Prerequisites

1. Install [Terraform](https://developer.hashicorp.com/terraform/downloads) (>= 1.5.0 recommended).
2. Install the [AWS CLI](https://aws.amazon.com/cli/).
3. Configure your AWS credentials using `aws configure` (or export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your environment). **Never commit AWS credentials to this repository.**

## Structure

- **`environments/dev/`**: Development environment configuration.
- **`modules/budget/`**: AWS Budget creation logic for cost protection.
- **`modules/iam/`**: IAM roles and policies based on least privilege principles.

## Getting Started (Development Environment)

Navigate to the development environment:
```bash
cd environments/dev
```

Initialize the Terraform working directory. This downloads necessary providers:
```bash
terraform init
```

### Checking Configuration

Format the code (this will automatically fix styling issues, use `-check` to just check):
```bash
terraform fmt -recursive ../../
```

Validate the syntax and configuration:
```bash
terraform validate
```

### Deployment

Generate and review an execution plan. This shows exactly what Terraform will do without actually applying the changes:
```bash
terraform plan
```

If the plan looks correct, apply the changes to your AWS account:
```bash
terraform apply
```
*(You will be prompted to confirm before the changes are made).*

### Tear Down

To destroy all resources created by this Terraform configuration (useful for keeping development costs at zero when not working):
```bash
terraform destroy
```

## Security Best Practices

1. **State Files**: `.tfstate` files can contain sensitive information. They are explicitly ignored in `.gitignore`. **Do not force commit them.**
2. **Variables**: Use `terraform.tfvars` for local variables. A `terraform.tfvars.example` is provided. Copy it to `terraform.tfvars` and customize it, but never commit `terraform.tfvars`.
3. **IAM**: We strictly enforce least privilege. Do not add `AdministratorAccess` unless explicitly required and documented.
