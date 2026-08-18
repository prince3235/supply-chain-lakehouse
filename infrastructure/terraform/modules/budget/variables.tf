variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "budget_limit" {
  description = "The monthly budget limit"
  type        = string
}

variable "currency" {
  description = "The currency for the budget"
  type        = string
  default     = "USD"
}

variable "alert_email_addresses" {
  description = "List of email addresses to send budget alerts to"
  type        = list(string)
}
