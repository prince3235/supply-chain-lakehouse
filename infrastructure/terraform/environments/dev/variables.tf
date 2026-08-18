variable "aws_region" {
  description = "AWS region for the development environment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "supply-chain-lake"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_owner" {
  description = "Owner tag value"
  type        = string
  default     = "data-engineering-team"
}

variable "cost_center" {
  description = "Cost center tag value"
  type        = string
  default     = "100-supply-chain"
}

variable "budget_limit" {
  description = "Monthly budget limit"
  type        = string
  default     = "10.0" # Keeps it extremely low for dev
}

variable "alert_email_addresses" {
  description = "Email addresses for budget alerts"
  type        = list(string)
}
