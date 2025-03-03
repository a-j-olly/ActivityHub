from flask import Blueprint, request, jsonify, current_app
from models.user import User
from utils.errors import error_response
from utils.auth import token_required, admin_required, parent_required
from utils.database import get_user_by_id, get_children_by_parent_id, update_user

# Create a blueprint for user routes
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    Get a user's profile by ID
    
    Args:
        user_id (str): User's ID
    
    Returns:
        JSON: User profile data
    """
    # Only allow access to your own profile or if you're a parent/admin
    from flask import g
    if g.user_id != user_id and g.user_role not in ['parent', 'admin']:
        # If the user is a parent, check if they're the parent of the requested user
        if g.user_role == 'parent':
            children = get_children_by_parent_id(g.user_id)
            child_ids = [child['user_id'] for child in children]
            if user_id not in child_ids:
                return error_response('FORBIDDEN', "You do not have permission to access this user's profile")
        else:
            return error_response('FORBIDDEN', "You do not have permission to access this user's profile")
    
    # Get the user from the database
    user = get_user_by_id(user_id)
    
    if not user:
        return error_response('NOT_FOUND', "User not found")
    
    # Return the user profile
    return jsonify({
        'user': user
    })

@users_bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user_profile(user_id):
    """
    Update a user's profile
    
    Args:
        user_id (str): User's ID
    
    Returns:
        JSON: Updated user profile
    """
    # Only allow updating your own profile or if you're a parent/admin
    from flask import g
    if g.user_id != user_id and g.user_role not in ['parent', 'admin']:
        # If the user is a parent, check if they're the parent of the requested user
        if g.user_role == 'parent':
            children = get_children_by_parent_id(g.user_id)
            child_ids = [child['user_id'] for child in children]
            if user_id not in child_ids:
                return error_response('FORBIDDEN', "You do not have permission to update this user's profile")
        else:
            return error_response('FORBIDDEN', "You do not have permission to update this user's profile")
    
    # Get request data
    data = request.get_json()
    if not data:
        return error_response('BAD_REQUEST', "No data provided for update")
    
    # Update the user
    try:
        updated_user = update_user(user_id, data)
        if not updated_user:
            return error_response('NOT_FOUND', "User not found or no valid updates provided")
        
        return jsonify({
            'message': 'User profile updated successfully',
            'user': updated_user
        })
    except Exception as e:
        current_app.logger.error(f"Error updating user profile: {str(e)}")
        return error_response('SERVER_ERROR', "Error updating user profile")

@users_bp.route('/children', methods=['GET'])
@parent_required
def get_children():
    """
    Get all children for the authenticated parent
    
    Returns:
        JSON: List of children profiles
    """
    from flask import g
    parent_id = g.user_id
    
    # Get all children for the parent
    children = get_children_by_parent_id(parent_id)
    
    return jsonify({
        'children': children
    })