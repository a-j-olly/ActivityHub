variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of the raw media S3 bucket"
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of the processed media S3 bucket"
  type        = string
}