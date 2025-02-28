# Raw Media Bucket
resource "aws_s3_bucket" "raw_media" {
  bucket = "${var.raw_bucket_name}-${var.environment}"

  tags = {
    Name = "${var.raw_bucket_name}-${var.environment}"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_media_lifecycle" {
  bucket = aws_s3_bucket.raw_media.id

  rule {
    id     = "delete-after-processing"
    status = "Enabled"

    expiration {
      days = 1 # Delete raw media after 24 hours
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_media_encryption" {
  bucket = aws_s3_bucket.raw_media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "raw_media_cors" {
  bucket = aws_s3_bucket.raw_media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET"]
    allowed_origins = ["*"] # This should be restricted to your application domain in production
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Processed Media Bucket
resource "aws_s3_bucket" "processed_media" {
  bucket = "${var.processed_bucket_name}-${var.environment}"

  tags = {
    Name = "${var.processed_bucket_name}-${var.environment}"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "processed_media_lifecycle" {
  bucket = aws_s3_bucket.processed_media.id

  rule {
    id     = "archive-old-media"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_media_encryption" {
  bucket = aws_s3_bucket.processed_media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "processed_media_cors" {
  bucket = aws_s3_bucket.processed_media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"] # This should be restricted to your application domain in production
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 Event Notification (placeholder for Lambda trigger)
resource "aws_s3_bucket_notification" "raw_media_notification" {
  bucket = aws_s3_bucket.raw_media.id

  depends_on = [
    aws_s3_bucket.raw_media
  ]

  # This will be configured once the Lambda function is created
  # lambda_function {
  #   lambda_function_arn = var.media_processor_lambda_arn
  #   events              = ["s3:ObjectCreated:*"]
  # }
}