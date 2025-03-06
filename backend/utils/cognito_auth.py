import json
import requests
import time
from functools import wraps
from jose import jwk, jwt
from jose.utils import base64url_decode
from flask import request, current_app, g
from utils.errors import error_response

# Cache for Cognito JWKS
_JWKS_CACHE = {}
_JWKS_CACHE_TIME = 0
_JWKS_CACHE_TTL = 3600  # 1 hour

def get_cognito_jwks():
    """
    Get the JSON Web Key Set (JWKS) from Cognito.
    Includes caching to avoid unnecessary requests.
    
    Returns:
        dict: JWKS
    """
    global _JWKS_CACHE, _JWKS_CACHE_TIME
    
    # Check if the cache is valid
    current_time = time.time()
    if _JWKS_CACHE and current_time - _JWKS_CACHE_TIME < _JWKS_CACHE_TTL:
        return _JWKS_CACHE
    
    # Fetch new JWKS
    region = current_app.config['COGNITO_REGION']
    pool_id = current_app.config['COGNITO_USER_POOL_ID']
    
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    
    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        
        _JWKS_CACHE = response.json()
        _JWKS_CACHE_TIME = current_time
        
        return _JWKS_CACHE
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching Cognito JWKS: {str(e)}")
        return None

# Fix in utils/cognito_auth.py
def verify_cognito_token(token):
    """
    Verify a Cognito JWT token
    
    Args:
        token (str): The JWT token to verify
    
    Returns:
        dict or None: The decoded token payload if valid, None otherwise
    """
    try:
        # Get JWKS
        jwks = get_cognito_jwks()
        if not jwks:
            return None
        
        # Get the header and payload from the token
        header = jwt.get_unverified_header(token)
        if not header or 'kid' not in header:
            return None
        
        # Find the key with matching kid
        key = None
        for jwk_key in jwks['keys']:
            if jwk_key['kid'] == header['kid']:
                key = jwk_key
                break
        
        if not key:
            return None
        
        # Get the claims for validation
        claims = jwt.get_unverified_claims(token)
        
        # Verify expiration
        if 'exp' in claims and time.time() > claims['exp']:
            return None
        
        # Verify token use
        token_use = claims.get('token_use')
        if token_use != 'access' and token_use != 'id':
            return None
        
        # Verify the audience (client ID)
        audience_valid = False
        if 'client_id' in claims and claims['client_id'] == current_app.config['COGNITO_APP_CLIENT_ID']:
            audience_valid = True
        elif 'aud' in claims and claims['aud'] == current_app.config['COGNITO_APP_CLIENT_ID']:
            audience_valid = True
        
        if not audience_valid:
            return None
        
        # Verify the signature
        public_key = jwk.construct(key)
        
        # Split token to get message and signature parts
        if token.count('.') != 2:
            return None
            
        message, encoded_signature = token.rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        
        # If signature verification fails, return None
        if not public_key.verify(message.encode('utf-8'), decoded_signature):
            return None
            
        # If all checks pass, return the claims
        return claims
        
    except Exception as e:
        current_app.logger.error(f"Error verifying Cognito token: {str(e)}")
        return None

def cognito_token_required(f):
    """
    Decorator to protect routes with Cognito JWT authentication
    
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
        
        # Verify token
        payload = verify_cognito_token(token)
        if not payload:
            return error_response('UNAUTHORIZED', 'Invalid or expired token')
        
        # Store user info in g object for the route to use
        if 'sub' in payload:
            g.user_id = payload['sub']
            
            # Get user role from Cognito 
            # Note: This might come from Cognito groups or custom attributes
            if 'cognito:groups' in payload and payload['cognito:groups']:
                g.user_role = payload['cognito:groups'][0]
            elif 'custom:role' in payload:
                g.user_role = payload['custom:role']
            else:
                g.user_role = 'user'  # Default role
        else:
            return error_response('UNAUTHORIZED', 'Invalid token format')
        
        return f(*args, **kwargs)
    
    return decorated

def cognito_admin_required(f):
    """
    Decorator to restrict routes to admin users
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function
    """
    @wraps(f)
    @cognito_token_required
    def decorated(*args, **kwargs):
        if g.user_role != 'admin':
            return error_response('FORBIDDEN', 'Admin privileges required')
        
        return f(*args, **kwargs)
    
    return decorated

def cognito_parent_required(f):
    """
    Decorator to restrict routes to parent users
    
    Args:
        f: The route function to protect
    
    Returns:
        function: The decorated function
    """
    @wraps(f)
    @cognito_token_required
    def decorated(*args, **kwargs):
        if g.user_role != 'parent' and g.user_role != 'admin':
            return error_response('FORBIDDEN', 'Parent privileges required')
        
        return f(*args, **kwargs)
    
    return decorated