from flask import Blueprint, request, jsonify, current_app
from models.user import User
from utils.errors import error_response
import re

# Create a blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
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
    
    # Check if user already exists
    existing_user = User.get_by_email(data['email'])
    if existing_user:
        return error_response('BAD_REQUEST', "User with this email already exists")
    
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
    
    # Create the user
    try:
        user = User.create(data['email'], data['name'], data['password'], role, parent_id)
        
        # Return success response
        return jsonify({
            'message': 'User registered successfully',
            'user': user
        }), 201
    except ValueError as e:
        return error_response('BAD_REQUEST', str(e))
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        return error_response('SERVER_ERROR', "Error registering user")

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token
    
    JSON Body:
        email (str): User's email
        password (str): User's password
    
    Returns:
        JSON: User data and JWT token
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
    
    # Authenticate the user
    user, token = User.authenticate(data['email'], data['password'])
    
    # Check if authentication was successful
    if not user or not token:
        return error_response('UNAUTHORIZED', "Invalid email or password")
    
    # Return success response with token
    return jsonify({
        'message': 'Login successful',
        'user': user,
        'token': token
    })
