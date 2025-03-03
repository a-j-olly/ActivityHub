import jwt
from functools import wraps
from flask import request, current_app, g
from datetime import datetime, timedelta
import uuid
import hashlib

from utils.errors import error_response

def generate_password_hash(password):
    """
    Generate a hash of the password using a secure algorithm
    
    Args:
        password (str): The password to hash
    
    Returns:
        str: The hashed password
    """
    # In a production environment, you should use a more secure hashing algorithm
    # with appropriate salt and work factor (e.g., bcrypt, Argon2)
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return f"{salt}${hashed_password}"

def verify_password(stored_password, provided_password):
    """
    Verify if the provided password matches the stored hashed password
    
    Args:
        stored_password (str): The stored hashed password
        provided_password (str): The password to verify
    
    Returns:
        bool: True if the password matches, False otherwise
    """
    salt, hashed_password = stored_password.split('$')
    calculated_hash = hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()
    return calculated_hash == hashed_password

def generate_jwt_token(user_id, role):
    """
    Generate a JWT token for the user
    
    Args:
        user_id (str): The user's ID
        role (str): The user's role (child, parent, or admin)
    
    Returns:
        str: JWT token
    """
    payload = {
        'sub': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def validate_jwt_token(token):
    """
    Validate a JWT token
    
    Args:
        token (str): The JWT token to validate
    
    Returns:
        dict or None: The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return error_response('UNAUTHORIZED', 'Missing authentication token')
        
        # Validate token
        payload = validate_jwt_token(token)
        if not payload:
            return error_response('UNAUTHORIZED', 'Invalid or expired token')
        
        # Store user info in g object for the route to use
        g.user_id = payload['sub']
        g.user_role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator to restrict routes to admin users
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.user_role != 'admin':
            return error_response('FORBIDDEN', 'Admin privileges required')
        
        return f(*args, **kwargs)
    
    return decorated

def parent_required(f):
    """
    Decorator to restrict routes to parent users
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.user_role != 'parent' and g.user_role != 'admin':
            return error_response('FORBIDDEN', 'Parent privileges required')
        
        return f(*args, **kwargs)
    
    return decorated
