# Set up Cognito
module "cognito" {
  source      = "./modules/cognito"
  app_name    = var.app_name
  environment = var.environment
  auto_verify = var.cognito_auto_verify
}

# Set up IAM roles
module "iam" {
  source             = "./modules/iam"
  app_name           = var.app_name
  environment        = var.environment
  dynamodb_table_arn = module.dynamodb.table_arn
  raw_bucket_arn     = module.s3.raw_bucket_arn
  processed_bucket_arn = module.s3.processed_bucket_arn
}

# Set up API Gateway
module "api_gateway" {
  source      = "./modules/api_gateway"
  api_name    = var.api_gateway_name
  environment = var.environment
  stage_name  = var.api_gateway_stage_name
}

# Set up Lambda function placeholder
module "lambda" {
  source                    = "./modules/lambda"
  app_name                  = var.app_name
  environment               = var.environment
  lambda_execution_role_arn = module.iam.lambda_execution_role_arn
  runtime                   = var.lambda_runtime
  timeout                   = var.lambda_timeout
  memory_size               = var.lambda_memory_size
  dynamodb_table_name       = module.dynamodb.table_name
  raw_bucket_name           = module.s3.raw_bucket_name
  processed_bucket_name     = module.s3.processed_bucket_name
}

# Set up DynamoDB
module "dynamodb" {
  source      = "./modules/dynamodb"
  table_name  = var.dynamodb_table_name
  environment = var.environment
  billing_mode = var.dynamodb_billing_mode
}

# Set up S3 buckets
module "s3" {
  source                = "./modules/s3"
  raw_bucket_name       = var.s3_raw_media_bucket_name
  processed_bucket_name = var.s3_processed_media_bucket_name
  environment           = var.environment
  # media_processor_lambda_arn will be set later
}