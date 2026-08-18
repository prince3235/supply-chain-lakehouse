data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.bucket_prefix}-${var.environment}-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.environment == "dev" ? true : false

  tags = {
    Name      = "${var.bucket_prefix}-${var.environment}"
    Component = "data-lake"
  }
}

# ------------------------------------------------------------------------------
# Object Ownership
# Preferred modern approach: BucketOwnerEnforced (disables ACLs)
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_ownership_controls" "data_lake_ownership" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# ------------------------------------------------------------------------------
# Public Access Block
# Ensures the bucket and objects cannot be made public
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_public_access_block" "data_lake_public_access_block" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------------------------------------------------------
# Encryption
# Simple cost-aware SSE-S3 encryption
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ------------------------------------------------------------------------------
# Versioning
# Protect against accidental overwrite/deletion
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ------------------------------------------------------------------------------
# Secure Transport Policy
# Deny HTTP requests, allow only HTTPS
# ------------------------------------------------------------------------------
data "aws_iam_policy_document" "secure_transport" {
  statement {
    sid       = "AllowSSLRequestsOnly"
    effect    = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["s3:*"]
    resources = [
      aws_s3_bucket.data_lake.arn,
      "${aws_s3_bucket.data_lake.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "data_lake_policy" {
  bucket = aws_s3_bucket.data_lake.id
  policy = data.aws_iam_policy_document.secure_transport.json

  # Ensure public access block is applied before policy
  depends_on = [aws_s3_bucket_public_access_block.data_lake_public_access_block]
}

# ------------------------------------------------------------------------------
# Lifecycle Configuration
# Cost control for dev environment
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_lifecycle_configuration" "data_lake_lifecycle" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "abort_incomplete_multipart_uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_incomplete_multipart_upload_days
    }
    filter {}
  }

  rule {
    id     = "expire_noncurrent_versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = var.retention_days
    }
    filter {}
  }
}
