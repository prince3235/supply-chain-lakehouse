provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "supply-chain-lakehouse"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.project_owner
      CostCenter  = var.cost_center
    }
  }
}
