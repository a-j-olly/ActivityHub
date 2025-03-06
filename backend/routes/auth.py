from flask import Blueprint, request, jsonify, current_app
import boto3
from botocore.exceptions import ClientError
from werkzeug.exceptions import BadRequest, Unauthorized
from utils.errors import error_response
import re

# Create a blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user with AWS Cognito
    
    JSON Body:
        email (str): User's email
        name (str): User's name
        password (str): User's password
        role (str, optional): User's role (child, parent, or admin). Defaults to 'child'.
        parent_id (str, optional): Parent's ID (required for child users). Defaults to None.
    
    Returns:
        JSON: User data and success message
    """
    # Get request data
    data = request.get_json(silent=True)
    if not data:
        return error_response('BAD_REQUEST', "Invalid JSON data")
    
    # Check if required fields are present
    required_fields = ['email', 'name', 'password']
    for field in required_fields:
        if field not in data:
            return error_response('BAD_REQUEST', f"Missing required field: {field}")
    
    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return error_response('BAD_REQUEST', "Invalid email format")
    
    # Validate password strength
    if len(data['password']) < 8:
        return error_response('BAD_REQUEST', "Password must be at least 8 characters long")
    
    # Get optional fields
    role = data.get('role', 'child')
    parent_id = data.get('parent_id')
    
    # Validate role
    valid_roles = ['child', 'parent', 'admin']
    if role not in valid_roles:
        return error_response('BAD_REQUEST', f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    # Validate parent_id is provided if role is 'child'
    if role == 'child' and not parent_id:
        return error_response('BAD_REQUEST', "Parent ID is required for child users")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # Register the user in Cognito
        response = client.sign_up(
            ClientId=current_app.config['COGNITO_APP_CLIENT_ID'],
            Username=data['email'],
            Password=data['password'],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': data['email']
                },
                {
                    'Name': 'name',
                    'Value': data['name']
                },
                {
                    'Name': 'custom:role',
                    'Value': role
                }
            ]
        )
        
        user_id = response['UserSub']
        
        # If the user is a child, add the parent ID as a custom attribute
        if role == 'child' and parent_id:
            client.admin_update_user_attributes(
                UserPoolId=current_app.config['COGNITO_USER_POOL_ID'],
                Username=data['email'],
                UserAttributes=[
                    {
                        'Name': 'custom:parentId',
                        'Value': parent_id
                    }
                ]
            )
        
        # Return success response
        user_data = {
            'user_id': user_id,
            'email': data['email'],
            'name': data['name'],
            'role': role
        }
        if role == 'child' and parent_id:
            user_data['parent_id'] = parent_id
            
        return jsonify({
            'message': 'User registered successfully',
            'user': user_data
        }), 201
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'UsernameExistsException':
            return error_response('BAD_REQUEST', "User with this email already exists")
        elif error_code == 'InvalidPasswordException':
            return error_response('BAD_REQUEST', str(e))
        else:
            current_app.logger.error(f"Error registering user: {str(e)}")
            return error_response('SERVER_ERROR', "Error registering user")

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user with AWS Cognito and return JWT tokens
    
    JSON Body:
        email (str): User's email
        password (str): User's password
    
    Returns:
        JSON: User data and JWT tokens
    """
    # Get request data
    data = request.get_json(silent=True)
    if not data:
        return error_response('BAD_REQUEST', "Invalid JSON data")
    
    # Check if required fields are present
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return error_response('BAD_REQUEST', f"Missing required field: {field}")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # Authenticate the user
        response = client.initiate_auth(
            ClientId=current_app.config['COGNITO_APP_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': data['email'],
                'PASSWORD': data['password']
            }
        )
        
        # Get tokens from the response
        tokens = response['AuthenticationResult']
        
        # Get the user's attributes
        user_response = client.get_user(
            AccessToken=tokens['AccessToken']
        )
        
        # Extract user data from attributes
        user_data = {
            'user_id': None,
            'email': data['email'],
            'name': None,
            'role': None
        }
        
        for attr in user_response['UserAttributes']:
            if attr['Name'] == 'sub':
                user_data['user_id'] = attr['Value']
            elif attr['Name'] == 'name':
                user_data['name'] = attr['Value']
            elif attr['Name'] == 'custom:role':
                user_data['role'] = attr['Value']
            elif attr['Name'] == 'custom:parentId' and user_data['role'] == 'child':
                user_data['parent_id'] = attr['Value']
        
        # Return success response with tokens
        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'tokens': {
                'id_token': tokens['IdToken'],
                'access_token': tokens['AccessToken'],
                'refresh_token': tokens['RefreshToken'],
                'expires_in': tokens['ExpiresIn']
            }
        })
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
            return error_response('UNAUTHORIZED', "Invalid email or password")
        else:
            current_app.logger.error(f"Error during login: {str(e)}")
            return error_response('SERVER_ERROR', "Error during login")

@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """
    Refresh the JWT token using the refresh token
    
    JSON Body:
        refresh_token (str): Refresh token
    
    Returns:
        JSON: New JWT tokens
    """
    # Get request data
    data = request.get_json(silent=True)
    if not data or 'refresh_token' not in data:
        return error_response('BAD_REQUEST', "Refresh token is required")
    
    # Initialize Cognito client
    client = boto3.client('cognito-idp', 
                         region_name=current_app.config['COGNITO_REGION'])
    
    try:
        # Refresh the token
        response = client.initiate_auth(
            ClientId=current_app.config['COGNITO_APP_CLIENT_ID'],
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': data['refresh_token']
            }
        )
        
        # Get tokens from the response
        tokens = response['AuthenticationResult']
        
        # Return success response with tokens
        return jsonify({
            'message': 'Token refreshed successfully',
            'tokens': {
                'id_token': tokens['IdToken'],
                'access_token': tokens['AccessToken'],
                'expires_in': tokens['ExpiresIn']
            }
        })
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NotAuthorizedException':
            return error_response('UNAUTHORIZED', "Invalid or expired refresh token")
        else:
            current_app.logger.error(f"Error refreshing token: {str(e)}")
            return error_response('SERVER_ERROR', "Error refreshing token")