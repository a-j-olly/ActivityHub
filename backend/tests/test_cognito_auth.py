import pytest
import time
import jwt
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from utils.cognito_auth import (
    get_cognito_jwks,
    verify_cognito_token,
    cognito_token_required,
    cognito_admin_required,
    cognito_parent_required
)

# Sample JWKS for testing
MOCK_JWKS = {
    "keys": [
        {
            "kid": "test-key-id",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "sample-modulus",
            "e": "AQAB"
        }
    ]
}

# Sample JWT payload for testing
MOCK_JWT_PAYLOAD = {
    "sub": "test-user-id",
    "email": "test@example.com",
    "custom:role": "parent",
    "exp": int(time.time()) + 3600,
    "iat": int(time.time()),
    "token_use": "access",
    "client_id": "test-client-id"
}

class TestCognitoAuth:
    def test_get_cognito_jwks_with_cache(self, app):
        """Test getting JWKS with caching."""
        with app.app_context():
            # Set up test configuration
            app.config['COGNITO_REGION'] = 'us-west-2'
            app.config['COGNITO_USER_POOL_ID'] = 'us-west-2_test'
            
            # Mock the requests.get call
            with patch('utils.cognito_auth.requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = MOCK_JWKS
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                # First call should make the request
                result = get_cognito_jwks()
                assert result == MOCK_JWKS
                assert mock_get.call_count == 1
                
                # Second call should use cache
                result = get_cognito_jwks()
                assert result == MOCK_JWKS
                assert mock_get.call_count == 1  # No additional call
    
    def test_verify_cognito_token(self, app):
        """Test token verification."""
        with app.app_context():
            # Set up test configuration
            app.config['COGNITO_REGION'] = 'us-west-2'
            app.config['COGNITO_USER_POOL_ID'] = 'us-west-2_test'
            app.config['COGNITO_APP_CLIENT_ID'] = 'test-client-id'
            
            # Create a mock token
            mock_token = "header.payload.signature"
            
            # Mock get_cognito_jwks
            with patch('utils.cognito_auth.get_cognito_jwks') as mock_get_jwks:
                mock_get_jwks.return_value = MOCK_JWKS
                
                # Mock jwt.get_unverified_header
                with patch('utils.cognito_auth.jwt.get_unverified_header') as mock_get_header:
                    mock_get_header.return_value = {"kid": "test-key-id", "alg": "RS256"}
                    
                    # Mock jwt.get_unverified_claims
                    with patch('utils.cognito_auth.jwt.get_unverified_claims') as mock_get_claims:
                        mock_get_claims.return_value = MOCK_JWT_PAYLOAD
                        
                        # Mock jwk.construct
                        with patch('utils.cognito_auth.jwk.construct') as mock_construct:
                            mock_public_key = MagicMock()
                            mock_public_key.verify.return_value = True
                            mock_construct.return_value = mock_public_key
                            
                            # Mock base64url_decode - this avoids needing to patch token.rsplit
                            with patch('utils.cognito_auth.base64url_decode') as mock_decode:
                                mock_decode.return_value = b'decoded-signature'
                                
                                # Test verification
                                result = verify_cognito_token(mock_token)
                                assert result == MOCK_JWT_PAYLOAD
    
    def test_verify_cognito_token_expired(self, app):
        """Test expired token verification."""
        with app.app_context():
            # Set up test configuration
            app.config['COGNITO_REGION'] = 'us-west-2'
            app.config['COGNITO_USER_POOL_ID'] = 'us-west-2_test'
            app.config['COGNITO_APP_CLIENT_ID'] = 'test-client-id'
            
            # Create expired token payload
            expired_payload = MOCK_JWT_PAYLOAD.copy()
            expired_payload['exp'] = int(time.time()) - 3600  # Expired 1 hour ago
            
            # Mock get_cognito_jwks
            with patch('utils.cognito_auth.get_cognito_jwks') as mock_get_jwks:
                mock_get_jwks.return_value = MOCK_JWKS
                
                # Mock jwt.get_unverified_header
                with patch('utils.cognito_auth.jwt.get_unverified_header') as mock_get_header:
                    mock_get_header.return_value = {"kid": "test-key-id", "alg": "RS256"}
                    
                    # Mock jwk.construct
                    with patch('utils.cognito_auth.jwk.construct') as mock_construct:
                        mock_public_key = MagicMock()
                        mock_public_key.verify.return_value = True
                        mock_construct.return_value = mock_public_key
                        
                        # Mock base64url_decode
                        with patch('utils.cognito_auth.base64url_decode') as mock_decode:
                            mock_decode.return_value = b'decoded-signature'
                            
                            # Mock jwt.get_unverified_claims
                            with patch('utils.cognito_auth.jwt.get_unverified_claims') as mock_get_claims:
                                mock_get_claims.return_value = expired_payload
                                
                                # Test verification
                                result = verify_cognito_token('mock-token')
                                assert result is None
    
    def test_cognito_token_required_decorator(self, app):
        """Test cognito_token_required decorator."""
        with app.app_context():
            # Create a Flask test client
            client = app.test_client()
            
            # Define a test endpoint with the decorator
            @app.route('/test-auth')
            @cognito_token_required
            def test_endpoint():
                return jsonify({'success': True})
            
            # Test without token
            response = client.get('/test-auth')
            assert response.status_code == 401
            
            # Test with token
            with patch('utils.cognito_auth.verify_cognito_token') as mock_verify:
                mock_verify.return_value = MOCK_JWT_PAYLOAD
                
                response = client.get('/test-auth', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 200
                
                # Test invalid token
                mock_verify.return_value = None
                
                response = client.get('/test-auth', headers={
                    'Authorization': 'Bearer invalid-token'
                })
                assert response.status_code == 401
    
    def test_cognito_admin_required_decorator(self, app):
        """Test cognito_admin_required decorator."""
        with app.app_context():
            # Create a Flask test client
            client = app.test_client()
            
            # Define a test endpoint with the decorator
            @app.route('/test-admin')
            @cognito_admin_required
            def test_endpoint():
                return jsonify({'success': True})
            
            # Test with admin user
            with patch('utils.cognito_auth.verify_cognito_token') as mock_verify:
                admin_payload = MOCK_JWT_PAYLOAD.copy()
                admin_payload['custom:role'] = 'admin'
                mock_verify.return_value = admin_payload
                
                response = client.get('/test-admin', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 200
                
                # Test with non-admin user
                parent_payload = MOCK_JWT_PAYLOAD.copy()
                parent_payload['custom:role'] = 'parent'
                mock_verify.return_value = parent_payload
                
                response = client.get('/test-admin', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 403
    
    def test_cognito_parent_required_decorator(self, app):
        """Test cognito_parent_required decorator."""
        with app.app_context():
            # Create a Flask test client
            client = app.test_client()
            
            # Define a test endpoint with the decorator
            @app.route('/test-parent')
            @cognito_parent_required
            def test_endpoint():
                return jsonify({'success': True})
            
            # Test with parent user
            with patch('utils.cognito_auth.verify_cognito_token') as mock_verify:
                parent_payload = MOCK_JWT_PAYLOAD.copy()
                parent_payload['custom:role'] = 'parent'
                mock_verify.return_value = parent_payload
                
                response = client.get('/test-parent', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 200
                
                # Test with admin user (should also work)
                admin_payload = MOCK_JWT_PAYLOAD.copy()
                admin_payload['custom:role'] = 'admin'
                mock_verify.return_value = admin_payload
                
                response = client.get('/test-parent', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 200
                
                # Test with child user
                child_payload = MOCK_JWT_PAYLOAD.copy()
                child_payload['custom:role'] = 'child'
                mock_verify.return_value = child_payload
                
                response = client.get('/test-parent', headers={
                    'Authorization': 'Bearer mock-token'
                })
                assert response.status_code == 403