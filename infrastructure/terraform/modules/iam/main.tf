# ------------------------------------------------------------------------------
# Developer Identity Role
# Used by developers/engineers. Has least privilege needed for dev work.
# ------------------------------------------------------------------------------
resource "aws_iam_role" "developer" {
  name = "${var.project_name}-${var.environment}-developer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          # In a real scenario, this would be an Identity Provider or specific users
          # Here we allow the current account to assume this role
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      },
    ]
  })
}

# Attach basic ViewOnlyAccess to developer for safety
resource "aws_iam_role_policy_attachment" "developer_view_only" {
  role       = aws_iam_role.developer.name
  policy_arn = "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
}

# ------------------------------------------------------------------------------
# Infrastructure Role
# Used by CI/CD or Terraform to provision infrastructure
# ------------------------------------------------------------------------------
resource "aws_iam_role" "infrastructure" {
  name = "${var.project_name}-${var.environment}-infra-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      },
    ]
  })
}

# ------------------------------------------------------------------------------
# S3 Access Role
# Used for specific data lake interactions, independent of admin access
# ------------------------------------------------------------------------------
resource "aws_iam_role" "s3_access" {
  name = "${var.project_name}-${var.environment}-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      },
    ]
  })
}

# ------------------------------------------------------------------------------
# Databricks Integration Role
# Used by Databricks workspace to access AWS resources (like S3 Data Lake)
# ------------------------------------------------------------------------------
resource "aws_iam_role" "databricks" {
  name = "${var.project_name}-${var.environment}-databricks-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      },
    ]
  })
}

data "aws_caller_identity" "current" {}
