import os
from datetime import timedelta

# Environment configuration
ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = ENV == 'development'

# Application configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Change in production
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')  # Change in production
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

# AWS configuration
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')

# DynamoDB configuration
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ActivityHub-staging')

# S3 configuration
S3_RAW_BUCKET = os.environ.get('S3_RAW_BUCKET', 'activityhub-media-raw-staging')
S3_PROCESSED_BUCKET = os.environ.get('S3_PROCESSED_BUCKET', 'activityhub-media-processed-staging')

# API configuration
API_PREFIX = '/api'

# Cognito configuration
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID', '')
COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID', '')
COGNITO_REGION = os.environ.get('COGNITO_REGION', AWS_REGION)

# Error messages
ERROR_MESSAGES = {
    'BAD_REQUEST': 'Invalid request data',
    'UNAUTHORIZED': 'Authentication required',
    'FORBIDDEN': 'You do not have permission to perform this action',
    'NOT_FOUND': 'Resource not found',
    'SERVER_ERROR': 'An unexpected error occurred'
}