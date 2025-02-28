output "raw_bucket_name" {
  description = "Name of the raw media S3 bucket"
  value       = aws_s3_bucket.raw_media.bucket
}

output "raw_bucket_arn" {
  description = "ARN of the raw media S3 bucket"
  value       = aws_s3_bucket.raw_media.arn
}

output "processed_bucket_name" {
  description = "Name of the processed media S3 bucket"
  value       = aws_s3_bucket.processed_media.bucket
}

output "processed_bucket_arn" {
  description = "ARN of the processed media S3 bucket"
  value       = aws_s3_bucket.processed_media.arn
}