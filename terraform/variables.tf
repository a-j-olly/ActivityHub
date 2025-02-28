# General AWS variables
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Deployment environment (staging or production)"
  type        = string
  default     = "staging"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "activityhub"
}

# Cognito variables
variable "cognito_user_pool_name" {
  description = "Name of the Cognito User Pool"
  type        = string
  default     = "activityhub-users"
}

variable "cognito_auto_verify" {
  description = "Auto verify email or phone"
  type        = bool
  default     = true
}

# DynamoDB variables
variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
  default     = "ActivityHub"
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string
  default     = "PAY_PER_REQUEST"
}

# S3 variables 
variable "s3_raw_media_bucket_name" {
  description = "Name of the S3 bucket for raw media uploads"
  type        = string
  default     = "activityhub-media-raw"
}

variable "s3_processed_media_bucket_name" {
  description = "Name of the S3 bucket for processed media"
  type        = string
  default     = "activityhub-media-processed"
}

# API Gateway variables
variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "activityhub-api"
}

variable "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  type        = string
  default     = "v1"
}

# Lambda variables
variable "lambda_runtime" {
  description = "Runtime for Lambda functions"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 256
}