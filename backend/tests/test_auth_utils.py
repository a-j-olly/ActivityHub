import pytest
import jwt
from datetime import datetime, timedelta

from utils.auth import (
    generate_password_hash,
    verify_password,
    generate_jwt_token,
    validate_jwt_token
)

class TestAuthUtils:
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification functionality."""
        # Arrange
        password = "secure_password123"
        
        # Act
        hashed_password = generate_password_hash(password)
        verify_correct = verify_password(hashed_password, password)
        verify_incorrect = verify_password(hashed_password, "wrong_password")
        
        # Assert
        assert hashed_password != password  # Hash should not be the plaintext
        assert "$" in hashed_password  # Should have salt separator
        assert verify_correct is True
        assert verify_incorrect is False
    
    def test_hash_uniqueness(self):
        """Test that the same password produces different hashes due to salt."""
        # Arrange
        password = "secure_password123"
        
        # Act
        hash1 = generate_password_hash(password)
        hash2 = generate_password_hash(password)
        
        # Assert
        assert hash1 != hash2  # Hashes should be different due to different salts
        assert verify_password(hash1, password)  # But both verify correctly
        assert verify_password(hash2, password)
    
    def test_jwt_token_generation_and_validation(self, app):
        """Test JWT token generation and validation."""
        # We need app context for current_app.config
        with app.app_context():
            # Arrange
            user_id = "test123"
            role = "parent"
            
            # Act
            token = generate_jwt_token(user_id, role)
            payload = validate_jwt_token(token)
            
            # Assert
            assert token is not None
            assert isinstance(token, str)
            assert payload is not None
            assert payload["sub"] == user_id
            assert payload["role"] == role
            assert "exp" in payload
            assert "iat" in payload
    
    def test_expired_token_validation(self, app, monkeypatch):
        """Test validation of expired tokens."""
        # We need app context for current_app.config
        with app.app_context():
            # Arrange
            user_id = "test123"
            role = "parent"
            
            # Create an expired token by monkeypatching datetime
            original_datetime = datetime
            
            class MockDatetime:
                @classmethod
                def utcnow(cls):
                    # Return a time from the past
                    return original_datetime.utcnow() - timedelta(hours=2)
            
            # Apply the monkeypatch for token generation
            monkeypatch.setattr('utils.auth.datetime', MockDatetime)
            
            # Generate token with the mocked time (it will be already expired)
            token = generate_jwt_token(user_id, role)
            
            # Restore the original datetime for validation
            monkeypatch.setattr('utils.auth.datetime', original_datetime)
            
            # Act
            payload = validate_jwt_token(token)
            
            # Assert
            assert payload is None  # Should be None for expired token
    
    def test_invalid_token_validation(self, app):
        """Test validation of invalid or tampered tokens."""
        # We need app context for current_app.config
        with app.app_context():
            # Arrange - Generating a valid token first
            user_id = "test123"
            role = "parent"
            valid_token = generate_jwt_token(user_id, role)
            
            # Tamper with the token
            tampered_token = valid_token[:-5] + "xxxxx"
            
            # Act
            payload = validate_jwt_token(tampered_token)
            
            # Assert
            assert payload is None
    
    def test_token_format_and_content(self, app):
        """Test the format and content of the generated JWT token."""
        # We need app context for current_app.config
        with app.app_context():
            # Arrange
            user_id = "test123"
            role = "admin"
            
            # Act
            token = generate_jwt_token(user_id, role)
            
            # Manually decode without verification to check structure
            # (This is just for testing the structure, not for validation)
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Assert
            assert decoded["sub"] == user_id
            assert decoded["role"] == role
            assert isinstance(decoded["exp"], int)
            assert isinstance(decoded["iat"], int)
            assert decoded["exp"] > decoded["iat"]  # Expiry should be after issued at
