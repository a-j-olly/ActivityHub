from utils.database import create_user, get_user_by_email, get_user_by_id
from utils.auth import generate_password_hash, verify_password, generate_jwt_token

class User:
    """
    User model for handling user operations
    """
    
    @staticmethod
    def create(email, name, password, role='child', parent_id=None):
        """
        Create a new user
        
        Args:
            email (str): User's email
            name (str): User's name
            password (str): User's password
            role (str, optional): User's role. Defaults to 'child'.
            parent_id (str, optional): Parent's ID for child users. Defaults to None.
        
        Returns:
            dict: The created user data
        """
        # Check if the role is valid
        valid_roles = ['child', 'parent', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Prepare user data
        user_data = {
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'role': role
        }
        
        # Add parent ID if role is child
        if role == 'child' and parent_id:
            user_data['parent_id'] = parent_id
        
        # Create the user
        return create_user(user_data)
    
    @staticmethod
    def authenticate(email, password):
        """
        Authenticate a user
        
        Args:
            email (str): User's email
            password (str): User's password
        
        Returns:
            tuple: (user_data, token) if authentication is successful, (None, None) otherwise
        """
        # Get the user by email
        user = get_user_by_email(email)
        
        # Check if user exists and password is correct
        if user and verify_password(user['password_hash'], password):
            # Remove password_hash from user data
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}
            
            # Generate JWT token
            token = generate_jwt_token(user['user_id'], user['role'])
            
            return user_data, token
        
        return None, None
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get a user by ID
        
        Args:
            user_id (str): User's ID
        
        Returns:
            dict or None: User data if found, None otherwise
        """
        return get_user_by_id(user_id)
    
    @staticmethod
    def get_by_email(email):
        """
        Get a user by email
        
        Args:
            email (str): User's email
        
        Returns:
            dict or None: User data if found, None otherwise
        """
        user = get_user_by_email(email)
        
        # Remove password_hash from user data if user exists
        if user:
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}
            return user_data
        
        return None
