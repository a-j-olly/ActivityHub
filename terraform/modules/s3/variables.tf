variable "raw_bucket_name" {
  description = "Name of the S3 bucket for raw media uploads"
  type        = string
}

variable "processed_bucket_name" {
  description = "Name of the S3 bucket for processed media"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "media_processor_lambda_arn" {
  description = "ARN of the media processor Lambda function"
  type        = string
  default     = null
}