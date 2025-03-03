import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import current_app
import uuid
import time

# Initialize DynamoDB client
def get_dynamodb_client():
    """
    Get a DynamoDB client
    
    Returns:
        boto3.client: DynamoDB client
    """
    return boto3.client(
        'dynamodb',
        region_name=current_app.config['AWS_REGION']
    )

def get_dynamodb_resource():
    """
    Get a DynamoDB resource
    
    Returns:
        boto3.resource: DynamoDB resource
    """
    return boto3.resource(
        'dynamodb',
        region_name=current_app.config['AWS_REGION']
    )

def get_table():
    """
    Get the DynamoDB table
    
    Returns:
        boto3.resource.Table: DynamoDB table
    """
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(current_app.config['DYNAMODB_TABLE'])

def generate_id():
    """
    Generate a unique ID
    
    Returns:
        str: Unique ID
    """
    return str(uuid.uuid4())

# User operations
def create_user(user_data):
    """
    Create a new user in DynamoDB
    
    Args:
        user_data (dict): User data including email, name, role, etc.
    
    Returns:
        dict: The created user data
    """
    table = get_table()
    
    # Generate a unique ID for the user
    user_id = generate_id()
    timestamp = int(time.time())
    
    # Create the item to store in DynamoDB
    item = {
        'PK': f"USER#{user_id}",
        'SK': 'PROFILE',
        'EntityType': 'USER',
        'GSI1PK': f"EMAIL#{user_data['email'].lower()}",
        'GSI1SK': 'USER',
        'UserId': user_id,
        'Email': user_data['email'].lower(),
        'Name': user_data['name'],
        'Role': user_data['role'],
        'PasswordHash': user_data['password_hash'],
        'CreatedAt': timestamp,
        'UpdatedAt': timestamp
    }
    
    # Add optional fields if they exist
    if 'parent_id' in user_data and user_data['role'] == 'child':
        item['ParentId'] = user_data['parent_id']
    
    # Put the item in the table
    table.put_item(Item=item)
    
    # Return the user data (excluding password hash)
    return {
        'user_id': user_id,
        'email': user_data['email'],
        'name': user_data['name'],
        'role': user_data['role'],
        'created_at': timestamp
    }

def get_user_by_email(email):
    """
    Get a user by email
    
    Args:
        email (str): User's email
    
    Returns:
        dict or None: User data if found, None otherwise
    """
    table = get_table()
    
    # Query the GSI1 index to find the user by email
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression=Key('GSI1PK').eq(f"EMAIL#{email.lower()}") & Key('GSI1SK').eq('USER')
    )
    
    # Return the user if found
    if response['Items']:
        item = response['Items'][0]
        return {
            'user_id': item['UserId'],
            'email': item['Email'],
            'name': item['Name'],
            'role': item['Role'],
            'password_hash': item['PasswordHash'],
            'created_at': item['CreatedAt']
        }
    
    return None

def get_user_by_id(user_id):
    """
    Get a user by ID
    
    Args:
        user_id (str): User's ID
    
    Returns:
        dict or None: User data if found, None otherwise
    """
    table = get_table()
    
    # Get the user by ID
    response = table.get_item(
        Key={
            'PK': f"USER#{user_id}",
            'SK': 'PROFILE'
        }
    )
    
    # Return the user if found
    if 'Item' in response:
        item = response['Item']
        return {
            'user_id': item['UserId'],
            'email': item['Email'],
            'name': item['Name'],
            'role': item['Role'],
            'created_at': item['CreatedAt']
        }
    
    return None
