output "budget_arn" {
  description = "The ARN of the AWS Budget"
  value       = module.budget.budget_arn
}

output "developer_role_arn" {
  description = "The ARN of the Developer role"
  value       = module.iam.developer_role_arn
}

output "infrastructure_role_arn" {
  description = "The ARN of the Infrastructure role"
  value       = module.iam.infrastructure_role_arn
}

output "s3_access_role_arn" {
  description = "The ARN of the S3 Access role"
  value       = module.iam.s3_access_role_arn
}

output "databricks_role_arn" {
  description = "The ARN of the Databricks Integration role"
  value       = module.iam.databricks_role_arn
}

output "data_lake_bucket_name" {
  description = "The name of the S3 Data Lake bucket"
  value       = module.data_lake.bucket_name
}

output "data_lake_bucket_arn" {
  description = "The ARN of the S3 Data Lake bucket"
  value       = module.data_lake.bucket_arn
}
