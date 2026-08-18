output "bucket_name" {
  description = "Name of the S3 Data Lake bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 Data Lake bucket"
  value       = aws_s3_bucket.data_lake.arn
}

output "bucket_region" {
  description = "AWS region of the S3 Data Lake bucket"
  value       = aws_s3_bucket.data_lake.region
}
