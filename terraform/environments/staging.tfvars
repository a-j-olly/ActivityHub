aws_region = "eu-west-2"
environment = "staging"
app_name = "activityhub"

# Cognito variables
cognito_user_pool_name = "activityhub-users"
cognito_auto_verify = true

# DynamoDB variables
dynamodb_table_name = "ActivityHub"
dynamodb_billing_mode = "PAY_PER_REQUEST"

# S3 variables
s3_raw_media_bucket_name = "activityhub-media-raw"
s3_processed_media_bucket_name = "activityhub-media-processed"

# API Gateway variables
api_gateway_name = "activityhub-api"
api_gateway_stage_name = "v1"

# Lambda variables
lambda_runtime = "python3.9"
lambda_timeout = 30
lambda_memory_size = 256