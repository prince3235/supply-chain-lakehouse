output "budget_arn" {
  description = "The ARN of the AWS Budget"
  value       = aws_budgets_budget.monthly_budget.arn
}

output "budget_id" {
  description = "The ID of the AWS Budget"
  value       = aws_budgets_budget.monthly_budget.id
}
