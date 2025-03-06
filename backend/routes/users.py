from flask import Blueprint, request, jsonify, current_app, g
from utils.errors import error_response
from utils.cognito_auth import cognito_token_required, cognito_admin_required, cognito_parent_required
import boto3
import time

# Create a blueprint for user routes
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/<user_id>', methods=['GET'])
@cognito_token_required
def get_user(user_id):
    """
    Get a user's profile by ID from Cognito
    
    Args:
        user_id (str): User's ID
    
    Returns:
        JSON: User profile data
    """
    # Only allow access to your own profile or if you're a parent/admin
    if g.user_id != user_id and g.user_role not in ['parent', 'admin']:
        # If the user is a parent, check if they're the parent of the requested user
        if g.user_role == 'parent':
            # We would need to query to find if this is their child
            # For now, let's just reject non-matching IDs
            return error_response('FORBIDDEN', "You do not have permission to access this user's profile")
        else:
            return error_response('FORBIDDEN', "You do not have permission to access this user's profile")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # We need to find the user by their ID (sub)
        # Since Cognito doesn't have a direct "get user by ID" API, we'll list users and filter
        response = client.list_users(
            UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
            Filter=f'sub = "{user_id}"'
        )
        
        if not response['Users'] or len(response['Users']) == 0:
            return error_response('NOT_FOUND', "User not found")
        
        # Get the first (and should be only) user
        cognito_user = response['Users'][0]
        
        # Extract user data from attributes
        user_data = {
            'user_id': user_id,
            'email': None,
            'name': None,
            'role': None,
            'created_at': cognito_user['UserCreateDate'].timestamp()
        }
        
        for attr in cognito_user['Attributes']:
            if attr['Name'] == 'email':
                user_data['email'] = attr['Value']
            elif attr['Name'] == 'name':
                user_data['name'] = attr['Value']
            elif attr['Name'] == 'custom:role':
                user_data['role'] = attr['Value']
            elif attr['Name'] == 'custom:parentId' and user_data.get('role') == 'child':
                user_data['parent_id'] = attr['Value']
        
        # Return the user profile
        return jsonify({
            'user': user_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user profile: {str(e)}")
        return error_response('SERVER_ERROR', "Error getting user profile")

@users_bp.route('/<user_id>', methods=['PUT'])
@cognito_token_required
def update_user_profile(user_id):
    """
    Update a user's profile in Cognito
    
    Args:
        user_id (str): User's ID
    
    Returns:
        JSON: Updated user profile
    """
    # Only allow updating your own profile or if you're a parent/admin
    if g.user_id != user_id and g.user_role not in ['parent', 'admin']:
        # If the user is a parent, check if they're the parent of the requested user
        if g.user_role == 'parent':
            # We would need to query to find if this is their child
            # For now, let's just reject non-matching IDs
            return error_response('FORBIDDEN', "You do not have permission to update this user's profile")
        else:
            return error_response('FORBIDDEN', "You do not have permission to update this user's profile")
    
    # Get request data
    data = request.get_json()
    if not data:
        return error_response('BAD_REQUEST', "No data provided for update")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # First find the user by their ID to get their username (email)
        list_response = client.list_users(
            UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
            Filter=f'sub = "{user_id}"'
        )
        
        if not list_response['Users'] or len(list_response['Users']) == 0:
            return error_response('NOT_FOUND', "User not found")
        
        # Get the username (email)
        username = None
        for attr in list_response['Users'][0]['Attributes']:
            if attr['Name'] == 'email':
                username = attr['Value']
                break
        
        if not username:
            return error_response('SERVER_ERROR', "Could not determine user's email")
        
        # Prepare attributes to update
        user_attributes = []
        
        # Add fields that can be updated
        if 'name' in data:
            user_attributes.append({
                'Name': 'name',
                'Value': data['name']
            })
        
        # Only admins can update roles
        if 'role' in data and g.user_role == 'admin':
            user_attributes.append({
                'Name': 'custom:role',
                'Value': data['role']
            })
        
        # Update the user in Cognito
        if user_attributes:
            client.admin_update_user_attributes(
                UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
                Username=username,
                UserAttributes=user_attributes
            )
            
            # Get the updated user
            get_response = client.admin_get_user(
                UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
                Username=username
            )
            
            # Extract user data from attributes
            user_data = {
                'user_id': user_id,
                'email': username,
                'name': None,
                'role': None,
                'updated_at': int(time.time())
            }
            
            for attr in get_response['UserAttributes']:
                if attr['Name'] == 'name':
                    user_data['name'] = attr['Value']
                elif attr['Name'] == 'custom:role':
                    user_data['role'] = attr['Value']
                elif attr['Name'] == 'custom:parentId' and user_data.get('role') == 'child':
                    user_data['parent_id'] = attr['Value']
            
            return jsonify({
                'message': 'User profile updated successfully',
                'user': user_data
            })
        else:
            return error_response('BAD_REQUEST', "No valid updates provided")
            
    except client.exceptions.UserNotFoundException:
        return error_response('NOT_FOUND', "User not found")
    except Exception as e:
        current_app.logger.error(f"Error updating user profile: {str(e)}")
        return error_response('SERVER_ERROR', "Error updating user profile")

@users_bp.route('/children', methods=['GET'])
@cognito_parent_required
def get_children():
    """
    Get all children for the authenticated parent from Cognito
    
    Returns:
        JSON: List of children profiles
    """
    parent_id = g.user_id
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # Find all users with custom:parentId matching this parent
        response = client.list_users(
            UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
            Filter=f'custom:parentId = "{parent_id}"'
        )
        
        children = []
        
        for cognito_user in response['Users']:
            # Extract user data from attributes
            user_data = {
                'user_id': None,
                'email': None,
                'name': None,
                'role': 'child',  # We know these are children
                'created_at': cognito_user['UserCreateDate'].timestamp()
            }
            
            for attr in cognito_user['Attributes']:
                if attr['Name'] == 'sub':
                    user_data['user_id'] = attr['Value']
                elif attr['Name'] == 'email':
                    user_data['email'] = attr['Value']
                elif attr['Name'] == 'name':
                    user_data['name'] = attr['Value']
            
            if user_data['user_id'] and user_data['email']:
                children.append(user_data)
        
        return jsonify({
            'children': children
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting children: {str(e)}")
        return error_response('SERVER_ERROR', "Error getting children")