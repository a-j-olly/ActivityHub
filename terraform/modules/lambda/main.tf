# Lambda Function Placeholder - This will be expanded as specific functions are developed
resource "aws_lambda_function" "placeholder" {
  function_name = "${var.app_name}-${var.environment}-placeholder"
  role          = var.lambda_execution_role_arn
  handler       = "lambda_function.lambda_handler"
  runtime       = var.runtime
  timeout       = var.timeout
  memory_size   = var.memory_size

  # Placeholder for code
  filename      = "${path.module}/placeholder_lambda.zip"
  
  environment {
    variables = {
      ENVIRONMENT        = var.environment
      DYNAMODB_TABLE     = var.dynamodb_table_name
      RAW_BUCKET         = var.raw_bucket_name
      PROCESSED_BUCKET   = var.processed_bucket_name
    }
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-placeholder"
  }
}

# Create a placeholder zip file for Lambda
resource "local_file" "placeholder_lambda_code" {
  content  = <<EOF
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Placeholder Lambda function'
    }
EOF
  filename = "${path.module}/lambda_function.py"
}

data "archive_file" "placeholder_lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/placeholder_lambda.zip"
  source_file = local_file.placeholder_lambda_code.filename

  depends_on = [
    local_file.placeholder_lambda_code
  ]
}