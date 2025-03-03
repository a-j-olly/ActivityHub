import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import current_app
import uuid
import time
import decimal
import json
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional

# Decimal values will be handled by the CustomJSONProvider in app.py

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

def create_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic function to create an item in DynamoDB
    
    Args:
        item (dict): The item to create
    
    Returns:
        dict: The created item
    """
    table = get_table()
    
    try:
        response = table.put_item(Item=item)
        return item
    except ClientError as e:
        current_app.logger.error(f"Error creating item in DynamoDB: {e}")
        raise

def get_item(pk: str, sk: str) -> Optional[Dict[str, Any]]:
    """
    Generic function to get an item from DynamoDB
    
    Args:
        pk (str): Partition key
        sk (str): Sort key
    
    Returns:
        dict or None: The item if found, None otherwise
    """
    table = get_table()
    
    try:
        response = table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        
        return response.get('Item')
    except ClientError as e:
        current_app.logger.error(f"Error getting item from DynamoDB: {e}")
        return None

def update_item(pk: str, sk: str, update_expression: str, expression_attribute_values: Dict[str, Any], 
                expression_attribute_names: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
    """
    Generic function to update an item in DynamoDB
    
    Args:
        pk (str): Partition key
        sk (str): Sort key
        update_expression (str): Update expression
        expression_attribute_values (dict): Expression attribute values
        expression_attribute_names (dict, optional): Expression attribute names
    
    Returns:
        dict or None: The updated item if successful, None otherwise
    """
    table = get_table()
    
    update_params = {
        'Key': {
            'PK': pk,
            'SK': sk
        },
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': expression_attribute_values,
        'ReturnValues': 'ALL_NEW'
    }
    
    if expression_attribute_names:
        update_params['ExpressionAttributeNames'] = expression_attribute_names
    
    try:
        response = table.update_item(**update_params)
        return response.get('Attributes')
    except ClientError as e:
        current_app.logger.error(f"Error updating item in DynamoDB: {e}")
        return None

def delete_item(pk: str, sk: str) -> bool:
    """
    Generic function to delete an item from DynamoDB
    
    Args:
        pk (str): Partition key
        sk (str): Sort key
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    table = get_table()
    
    try:
        table.delete_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        return True
    except ClientError as e:
        current_app.logger.error(f"Error deleting item from DynamoDB: {e}")
        return False

def query_items(index_name: str = None, key_condition_expression=None, 
               filter_expression=None, expression_attribute_values: Dict[str, Any] = None,
               expression_attribute_names: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """
    Generic function to query items from DynamoDB
    
    Args:
        index_name (str, optional): Name of the index to query. Defaults to None.
        key_condition_expression: Key condition expression
        filter_expression: Filter expression
        expression_attribute_values (dict, optional): Expression attribute values
        expression_attribute_names (dict, optional): Expression attribute names
    
    Returns:
        list: List of items matching the query
    """
    table = get_table()
    
    query_params = {}
    
    if index_name:
        query_params['IndexName'] = index_name
    
    if key_condition_expression:
        query_params['KeyConditionExpression'] = key_condition_expression
    
    if filter_expression:
        query_params['FilterExpression'] = filter_expression
    
    if expression_attribute_values:
        query_params['ExpressionAttributeValues'] = expression_attribute_values
    
    if expression_attribute_names:
        query_params['ExpressionAttributeNames'] = expression_attribute_names
    
    try:
        response = table.query(**query_params)
        return response.get('Items', [])
    except ClientError as e:
        current_app.logger.error(f"Error querying items from DynamoDB: {e}")
        return []

# User-specific operations
def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user in DynamoDB
    
    Args:
        user_data (dict): User data including email, name, role, etc.
    
    Returns:
        dict: The created user data
    """
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
        
        # Create relationship between child and parent
        parent_relation = {
            'PK': f"USER#{user_data['parent_id']}",
            'SK': f"CHILD#{user_id}",
            'EntityType': 'RELATIONSHIP',
            'GSI1PK': f"PARENT#{user_data['parent_id']}",
            'GSI1SK': f"CHILD#{user_id}",
            'ChildId': user_id,
            'ParentId': user_data['parent_id'],
            'CreatedAt': timestamp
        }
        try:
            create_item(parent_relation)
        except Exception as e:
            current_app.logger.warning(f"Failed to create parent-child relationship: {str(e)}")
    
    # Put the item in the table
    try:
        create_item(item)
    except Exception as e:
        current_app.logger.error(f"Failed to create user: {str(e)}")
        raise
    
    # Return the user data (excluding password hash)
    return {
        'user_id': user_id,
        'email': user_data['email'],
        'name': user_data['name'],
        'role': user_data['role'],
        'created_at': timestamp
    }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email
    
    Args:
        email (str): User's email
    
    Returns:
        dict or None: User data if found, None otherwise
    """
    # Query the GSI1 index to find the user by email
    items = query_items(
        index_name='GSI1',
        key_condition_expression=Key('GSI1PK').eq(f"EMAIL#{email.lower()}") & Key('GSI1SK').eq('USER')
    )
    
    # Return the user if found
    if items:
        item = items[0]
        return {
            'user_id': item['UserId'],
            'email': item['Email'],
            'name': item['Name'],
            'role': item['Role'],
            'password_hash': item['PasswordHash'],
            'created_at': item['CreatedAt']
        }
    
    return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID
    
    Args:
        user_id (str): User's ID
    
    Returns:
        dict or None: User data if found, None otherwise
    """
    # Get the user by ID
    item = get_item(f"USER#{user_id}", 'PROFILE')
    
    # Return the user if found
    if item:
        return {
            'user_id': item['UserId'],
            'email': item['Email'],
            'name': item['Name'],
            'role': item['Role'],
            'created_at': item['CreatedAt']
        }
    
    return None

def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a user in DynamoDB
    
    Args:
        user_id (str): User's ID
        updates (dict): Updates to apply to the user
    
    Returns:
        dict or None: The updated user data if successful, None otherwise
    """
    # Build update expression and attribute values
    update_parts = []
    expression_attribute_values = {
        ':updated_at': int(time.time())
    }
    expression_attribute_names = {
        '#updated_at': 'UpdatedAt'
    }
    
    for key, value in updates.items():
        # Skip certain fields that should not be updated directly
        if key in ['user_id', 'email', 'password_hash', 'created_at']:
            continue
        
        # Add to update expression and values
        field_name = key[0].upper() + key[1:]  # Convert camelCase to PascalCase for DynamoDB
        expression_attribute_names[f'#{key}'] = field_name
        update_parts.append(f'#{key} = :{key}')
        expression_attribute_values[f':{key}'] = value
    
    # Add UpdatedAt to update expression
    update_parts.append('#updated_at = :updated_at')
    
    # If there's nothing to update, return None
    if not update_parts:
        return None
    
    update_expression = 'SET ' + ', '.join(update_parts)
    
    # Update the item
    updated_item = update_item(
        pk=f"USER#{user_id}",
        sk='PROFILE',
        update_expression=update_expression,
        expression_attribute_values=expression_attribute_values,
        expression_attribute_names=expression_attribute_names
    )
    
    # Return the updated user data if successful
    if updated_item:
        return {
            'user_id': updated_item['UserId'],
            'email': updated_item['Email'],
            'name': updated_item['Name'],
            'role': updated_item['Role'],
            'created_at': updated_item['CreatedAt'],
            'updated_at': updated_item['UpdatedAt']
        }
    
    return None

def delete_user(user_id: str) -> bool:
    """
    Delete a user from DynamoDB
    
    Args:
        user_id (str): User's ID
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    # First get the user to check their role and related data
    user = get_user_by_id(user_id)
    if not user:
        return False
    
    # Delete the user's profile
    success = delete_item(f"USER#{user_id}", 'PROFILE')
    
    # If the user is a parent, we might need to handle their children
    # If the user is a child, we might need to update the parent's records
    # This would be implemented based on specific business requirements
    
    return success

def get_children_by_parent_id(parent_id: str) -> List[Dict[str, Any]]:
    """
    Get all children for a parent
    
    Args:
        parent_id (str): Parent's ID
    
    Returns:
        list: List of children data
    """
    # Query to find all children relationships for the parent
    items = query_items(
        key_condition_expression=Key('PK').eq(f"USER#{parent_id}") & Key('SK').begins_with('CHILD#')
    )
    
    # Get the full user data for each child
    children = []
    for item in items:
        child_id = item['ChildId']
        child_data = get_user_by_id(child_id)
        if child_data:
            children.append(child_data)
    
    return children