terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.20.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "aws_account_id" {
  type = string
}

# IAM Role for Unity Catalog
resource "aws_iam_role" "unity_catalog_role" {
  name = "databricks-uc-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::414364122586:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYCY"
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.aws_account_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "unity_catalog_s3_access" {
  name = "unity-catalog-s3-access-${var.environment}"
  role = aws_iam_role.unity_catalog_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

# Unity Catalog Storage Credential
resource "databricks_storage_credential" "aws_uc_credential" {
  name = "aws-uc-credential-${var.environment}"
  aws_iam_role {
    role_arn = aws_iam_role.unity_catalog_role.arn
  }
}

# Unity Catalog External Locations
resource "databricks_external_location" "raw_location" {
  name            = "s3-raw-${var.environment}"
  url             = "s3://${var.s3_bucket_name}/raw/"
  credential_name = databricks_storage_credential.aws_uc_credential.id
  comment         = "Raw ingestion location"
}

resource "databricks_external_location" "bronze_location" {
  name            = "s3-bronze-${var.environment}"
  url             = "s3://${var.s3_bucket_name}/bronze/"
  credential_name = databricks_storage_credential.aws_uc_credential.id
  comment         = "Bronze Delta Lake location"
}

# Unity Catalog Catalog
resource "databricks_catalog" "environment_catalog" {
  name    = "supply_chain_${var.environment}"
  comment = "Supply Chain Lakehouse ${var.environment} catalog"
}

# Unity Catalog Bronze Schema
resource "databricks_schema" "bronze_schema" {
  catalog_name = databricks_catalog.environment_catalog.id
  name         = "bronze"
  comment      = "Bronze layer for raw source data"
}
