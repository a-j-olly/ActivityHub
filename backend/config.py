import os
from datetime import timedelta

class DefaultConfig:
    """Default configuration for ActivityHub application."""
    # Environment configuration
    DEBUG = False
    TESTING = False
    
    # Application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Change in production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')  # Change in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # AWS configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
    
    # DynamoDB configuration
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ActivityHub')
    DYNAMODB_ENDPOINT_URL = os.environ.get('DYNAMODB_ENDPOINT_URL', None)
    
    # S3 configuration
    S3_RAW_BUCKET = os.environ.get('S3_RAW_BUCKET', 'activityhub-media-raw')
    S3_PROCESSED_BUCKET = os.environ.get('S3_PROCESSED_BUCKET', 'activityhub-media-processed')
    
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


class DevelopmentConfig(DefaultConfig):
    """Development configuration for ActivityHub application."""
    DEBUG = True
    
    # Development-specific settings
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ActivityHub-dev')
    S3_RAW_BUCKET = os.environ.get('S3_RAW_BUCKET', 'activityhub-media-raw-dev')
    S3_PROCESSED_BUCKET = os.environ.get('S3_PROCESSED_BUCKET', 'activityhub-media-processed-dev')
    
    # For local development, you might want to use local DynamoDB
    DYNAMODB_ENDPOINT_URL = os.environ.get('DYNAMODB_ENDPOINT_URL', None)


class TestingConfig(DefaultConfig):
    """Testing configuration for ActivityHub application."""
    TESTING = True
    DEBUG = False
    
    # Test-specific settings
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ActivityHub-test')
    S3_RAW_BUCKET = os.environ.get('S3_RAW_BUCKET', 'activityhub-media-raw-test')
    S3_PROCESSED_BUCKET = os.environ.get('S3_PROCESSED_BUCKET', 'activityhub-media-processed-test')
    
    # For testing, we'll often mock AWS services
    SERVER_NAME = "test.local"
    
    # Override secrets with test-specific values for predictability
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'


class ProductionConfig(DefaultConfig):
    """Production configuration for ActivityHub application."""
    # Production-specific settings
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ActivityHub-prod')
    S3_RAW_BUCKET = os.environ.get('S3_RAW_BUCKET', 'activityhub-media-raw-prod')
    S3_PROCESSED_BUCKET = os.environ.get('S3_PROCESSED_BUCKET', 'activityhub-media-processed-prod')
    
    # Ensure these are set in production environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Override with stricter settings for production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


# Configuration dictionary to map config name to config class
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DefaultConfig
}