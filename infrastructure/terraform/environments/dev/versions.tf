terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # NOTE: Local state is used for Phase 1 to prevent unexpected infrastructure costs.
  # For Phase 2+, remote state (S3 + DynamoDB) should be configured here.
}
