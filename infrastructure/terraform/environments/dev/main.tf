# -----------------------------------------------------------------------------
# Phase 1: AWS Cloud Foundation
# Development Environment
# -----------------------------------------------------------------------------

module "iam" {
  source       = "../../modules/iam"
  project_name = var.project_name
  environment  = var.environment
}

module "budget" {
  source                = "../../modules/budget"
  project_name          = var.project_name
  environment           = var.environment
  budget_limit          = var.budget_limit
  alert_email_addresses = var.alert_email_addresses
}

# -----------------------------------------------------------------------------
# Phase 2: AWS S3 Data Lake Foundation
# -----------------------------------------------------------------------------
module "data_lake" {
  source        = "../../modules/data-lake"
  bucket_prefix = var.project_name
  environment   = var.environment

  # Keeping noncurrent versions for 30 days in dev before expiring to save cost
  retention_days = 30
}
