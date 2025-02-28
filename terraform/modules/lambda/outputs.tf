output "placeholder_function_name" {
  description = "Name of the placeholder Lambda function"
  value       = aws_lambda_function.placeholder.function_name
}

output "placeholder_function_arn" {
  description = "ARN of the placeholder Lambda function"
  value       = aws_lambda_function.placeholder.arn
}