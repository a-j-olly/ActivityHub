import os
import pytest
import tempfile
import json
from flask import Flask
from werkzeug.security import generate_password_hash
import time

# Add the backend directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from utils.auth import generate_password_hash, generate_jwt_token


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Create app context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client using the app fixture."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_db(monkeypatch):
    """Mock the DynamoDB functions with an improved implementation."""
    # Dictionary to store our "database" items
    db_items = {}
    
    # Mock the DynamoDB resource
    class MockDynamoTable:
        def put_item(self, Item):
            # Create a copy of the item to avoid reference issues
            item_copy = {k: v for k, v in Item.items()}
            pk = item_copy['PK']
            sk = item_copy['SK']
            key = f"{pk}#{sk}"
            db_items[key] = item_copy
            return {}
        
        def get_item(self, Key):
            pk = Key['PK']
            sk = Key['SK']
            key = f"{pk}#{sk}"
            if key in db_items:
                return {"Item": db_items[key]}
            return {}
        
        def query(self, **kwargs):
            # Improved query implementation for testing
            results = []
            
            # Handle IndexName='GSI1' queries (e.g., email lookups)
            if 'IndexName' in kwargs and kwargs['IndexName'] == 'GSI1':
                # Extract the condition value for GSI1PK from KeyConditionExpression
                key_condition = kwargs.get('KeyConditionExpression', '')
                
                for item in db_items.values():
                    if 'GSI1PK' not in item or 'GSI1SK' not in item:
                        continue
                    
                    # Handle email lookups more explicitly
                    if 'EMAIL#' in str(key_condition) and item['GSI1PK'].startswith('EMAIL#'):
                        # Extract email from key condition
                        email_parts = str(key_condition).split('EMAIL#')
                        if len(email_parts) > 1:
                            email = email_parts[1].split("'")[0]
                            if item['GSI1PK'] == f"EMAIL#{email}" and item['GSI1SK'] == 'USER':
                                results.append(item)
            
            # Handle regular PK queries
            elif 'KeyConditionExpression' in kwargs:
                key_condition = kwargs.get('KeyConditionExpression', '')
                
                for item in db_items.values():
                    # Check for PK equality conditions
                    if 'PK' in item and 'PK' in str(key_condition):
                        # Extract PK value from the condition
                        pk_parts = str(key_condition).split('PK')
                        if len(pk_parts) > 1 and '.eq(' in pk_parts[1]:
                            pk_value = pk_parts[1].split('.eq(')[1].split(')')[0].strip("'")
                            
                            if item['PK'] == pk_value:
                                # Check for begins_with on SK
                                if 'begins_with' in str(key_condition) and 'SK' in item:
                                    # Extract the prefix
                                    prefix_parts = str(key_condition).split('begins_with')
                                    if len(prefix_parts) > 1:
                                        prefix = prefix_parts[1].split(',')[1].strip().strip("')")
                                        if item['SK'].startswith(prefix):
                                            results.append(item)
                                else:
                                    # If no SK condition or it matches
                                    results.append(item)
                            
            # Handle the 'EntityTypeIndex'
            elif 'IndexName' in kwargs and kwargs['IndexName'] == 'EntityTypeIndex':
                # Extract the condition value for EntityType from KeyConditionExpression
                key_condition = kwargs.get('KeyConditionExpression', '')
                
                for item in db_items.values():
                    # Check if item has EntityType field
                    if 'EntityType' in item:
                        # Handle entity type lookups with eq() condition
                        if 'EntityType' in str(key_condition) and '.eq(' in str(key_condition):
                            # Extract the entity type value from the condition
                            parts = str(key_condition).split('.eq(')
                            if len(parts) > 1:
                                entity_type = parts[1].split(')')[0].strip("'")
                                if item['EntityType'] == entity_type:
                                    results.append(item)
            
            # Simple full scan if no conditions specified
            else:
                results = list(db_items.values())
                    
            return {"Items": results}
        
        def update_item(self, **kwargs):
            # Improved update_item that actually updates the item
            pk = kwargs['Key']['PK']
            sk = kwargs['Key']['SK']
            key = f"{pk}#{sk}"
            
            if key not in db_items:
                return {}
            
            # Get the item
            item = db_items[key]
            
            # Apply updates (simplified)
            if 'UpdateExpression' in kwargs:
                update_expr = kwargs['UpdateExpression']
                attr_values = kwargs.get('ExpressionAttributeValues', {})
                attr_names = kwargs.get('ExpressionAttributeNames', {})
                
                # Parse SET operations
                if update_expr.startswith('SET'):
                    # Split by comma to handle multiple updates
                    updates = update_expr[4:].split(',')
                    for update in updates:
                        update = update.strip()
                        if '=' in update:
                            # Handle "#name = :name" format
                            left, right = update.split('=')
                            left = left.strip()
                            right = right.strip()
                            
                            # Handle attribute name references
                            if left.startswith('#'):
                                attr_key = attr_names.get(left, left)
                                attr_key = attr_key.replace('#', '')
                            else:
                                attr_key = left
                            
                            # Handle attribute value references
                            if right.startswith(':'):
                                attr_value = attr_values.get(right, right)
                            else:
                                attr_value = right
                            
                            # Apply the update (handle nested keys if needed)
                            if attr_key == 'name':
                                item['Name'] = attr_value
                            elif attr_key == 'Name':
                                item['Name'] = attr_value
                            elif attr_key == 'UpdatedAt':
                                item['UpdatedAt'] = attr_value
                            else:
                                # Generic update
                                item[attr_key] = attr_value
            
            # Return updated item for ALL_NEW
            if 'ReturnValues' in kwargs and kwargs['ReturnValues'] == 'ALL_NEW':
                return {"Attributes": item}
            
            return {}
        
        def delete_item(self, Key):
            pk = Key['PK']
            sk = Key['SK']
            key = f"{pk}#{sk}"
            
            if key in db_items:
                del db_items[key]
            
            return {}
    
    # Create a mock DynamoDB resource
    class MockDynamoDB:
        def Table(self, table_name):
            return MockDynamoTable()
    
    # Replace the real get_dynamodb_resource with our mock
    def mock_get_dynamodb_resource():
        return MockDynamoDB()
    
    # Replace the real get_table with our mock
    def mock_get_table():
        return MockDynamoDB().Table("ActivityHub-test")
    
    # Apply the monkeypatches
    monkeypatch.setattr('utils.database.get_dynamodb_resource', mock_get_dynamodb_resource)
    monkeypatch.setattr('utils.database.get_table', mock_get_table)
    
    return db_items


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    def _auth_headers(user_id, role='parent'):
        token = generate_jwt_token(user_id, role)
        return {'Authorization': f'Bearer {token}'}
    
    return _auth_headers


@pytest.fixture
def test_user(mock_db):
    """Create a test user for authentication tests."""
    user_id = 'testuser123'
    
    user_data = {
        'PK': f'USER#{user_id}',
        'SK': 'PROFILE',
        'EntityType': 'USER',
        'GSI1PK': 'EMAIL#test@example.com',
        'GSI1SK': 'USER',
        'UserId': user_id,
        'Email': 'test@example.com',
        'Name': 'Test User',
        'Role': 'parent',
        'PasswordHash': generate_password_hash('password123'),
        'CreatedAt': 1645123456,
        'UpdatedAt': 1645123456
    }
    
    # Add the user to our mock DB
    mock_db[f"{user_data['PK']}#{user_data['SK']}"] = user_data
    
    return {
        'user_id': user_id,
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'parent',
        'password': 'password123'
    }


@pytest.fixture
def test_child_user(mock_db, test_user):
    """Create a test child user for parent-child relationship tests."""
    child_id = 'childuser456'
    
    child_data = {
        'PK': f'USER#{child_id}',
        'SK': 'PROFILE',
        'EntityType': 'USER',
        'GSI1PK': 'EMAIL#child@example.com',
        'GSI1SK': 'USER',
        'UserId': child_id,
        'Email': 'child@example.com',
        'Name': 'Child User',
        'Role': 'child',
        'ParentId': test_user['user_id'],
        'PasswordHash': generate_password_hash('childpass123'),
        'CreatedAt': 1645123456,
        'UpdatedAt': 1645123456
    }
    
    # Add the child to our mock DB
    mock_db[f"{child_data['PK']}#{child_data['SK']}"] = child_data
    
    # Also add the parent-child relationship
    relationship_data = {
        'PK': f"USER#{test_user['user_id']}",
        'SK': f"CHILD#{child_id}",
        'EntityType': 'RELATIONSHIP',
        'GSI1PK': f"PARENT#{test_user['user_id']}",
        'GSI1SK': f"CHILD#{child_id}",
        'ChildId': child_id,
        'ParentId': test_user['user_id'],
        'CreatedAt': 1645123456
    }
    
    mock_db[f"{relationship_data['PK']}#{relationship_data['SK']}"] = relationship_data
    
    return {
        'user_id': child_id,
        'email': 'child@example.com',
        'name': 'Child User',
        'role': 'child',
        'password': 'childpass123',
        'parent_id': test_user['user_id']
    }