output "developer_role_arn" {
  description = "The ARN of the Developer role"
  value       = aws_iam_role.developer.arn
}

output "infrastructure_role_arn" {
  description = "The ARN of the Infrastructure role"
  value       = aws_iam_role.infrastructure.arn
}

output "s3_access_role_arn" {
  description = "The ARN of the S3 Access role"
  value       = aws_iam_role.s3_access.arn
}

output "databricks_role_arn" {
  description = "The ARN of the Databricks Integration role"
  value       = aws_iam_role.databricks.arn
}
