import pytest
import json
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

class TestAuthRoutes:
    def test_register_success(self, client):
        """Test successful user registration with Cognito."""
        # Arrange
        registration_data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'password123',
            'role': 'parent'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the sign_up response
            mock_client.sign_up.return_value = {
                'UserSub': 'test-user-id',
                'UserConfirmed': False
            }
            
            # Act
            response = client.post(
                '/api/register',
                data=json.dumps(registration_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'User registered successfully'
            assert 'user' in data
            assert data['user']['email'] == 'newuser@example.com'
            assert data['user']['name'] == 'New User'
            assert data['user']['role'] == 'parent'
            assert data['user']['user_id'] == 'test-user-id'
            
            # Verify Cognito was called with correct parameters
            mock_client.sign_up.assert_called_once()
            _, kwargs = mock_client.sign_up.call_args
            assert kwargs['Username'] == 'newuser@example.com'
            assert kwargs['Password'] == 'password123'
            
            # Verify attributes
            attrs = {attr['Name']: attr['Value'] for attr in kwargs['UserAttributes']}
            assert attrs['email'] == 'newuser@example.com'
            assert attrs['name'] == 'New User'
            assert attrs['custom:role'] == 'parent'
    
    def test_register_child_with_parent(self, client):
        """Test registering a child user with a parent ID."""
        # Arrange
        child_data = {
            'email': 'child@example.com',
            'name': 'Child User',
            'password': 'password123',
            'role': 'child',
            'parent_id': 'parent-user-id'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the sign_up response
            mock_client.sign_up.return_value = {
                'UserSub': 'child-user-id',
                'UserConfirmed': False
            }
            
            # Act
            response = client.post(
                '/api/register',
                data=json.dumps(child_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'User registered successfully'
            assert data['user']['role'] == 'child'
            assert data['user']['parent_id'] == 'parent-user-id'
            
            # Verify admin_update_user_attributes was called
            mock_client.admin_update_user_attributes.assert_called_once()
            _, kwargs = mock_client.admin_update_user_attributes.call_args
            attrs = {attr['Name']: attr['Value'] for attr in kwargs['UserAttributes']}
            assert attrs['custom:parentId'] == 'parent-user-id'
    
    def test_register_duplicate_email(self, client):
        """Test registration with an email that already exists."""
        # Arrange
        registration_data = {
            'email': 'existing@example.com',
            'name': 'Existing User',
            'password': 'password123',
            'role': 'parent'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the sign_up method to raise ClientError
            error_response = {
                'Error': {
                    'Code': 'UsernameExistsException',
                    'Message': 'User already exists'
                }
            }
            mock_client.sign_up.side_effect = ClientError(error_response, 'sign_up')
            
            # Act
            response = client.post(
                '/api/register',
                data=json.dumps(registration_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert data['message'] == "User with this email already exists"
    
    def test_login_success(self, client):
        """Test successful login."""
        # Arrange
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the initiate_auth response
            mock_client.initiate_auth.return_value = {
                'AuthenticationResult': {
                    'IdToken': 'mock-id-token',
                    'AccessToken': 'mock-access-token',
                    'RefreshToken': 'mock-refresh-token',
                    'ExpiresIn': 3600
                }
            }
            
            # Mock the get_user response
            mock_client.get_user.return_value = {
                'Username': 'test@example.com',
                'UserAttributes': [
                    {'Name': 'sub', 'Value': 'test-user-id'},
                    {'Name': 'email', 'Value': 'test@example.com'},
                    {'Name': 'name', 'Value': 'Test User'},
                    {'Name': 'custom:role', 'Value': 'parent'}
                ]
            }
            
            # Act
            response = client.post(
                '/api/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Login successful'
            assert data['user']['email'] == 'test@example.com'
            assert data['user']['name'] == 'Test User'
            assert data['user']['role'] == 'parent'
            assert data['tokens']['id_token'] == 'mock-id-token'
            assert data['tokens']['access_token'] == 'mock-access-token'
            assert data['tokens']['refresh_token'] == 'mock-refresh-token'
            
            # Verify Cognito was called with correct parameters
            mock_client.initiate_auth.assert_called_once()
            _, kwargs = mock_client.initiate_auth.call_args
            assert kwargs['AuthFlow'] == 'USER_PASSWORD_AUTH'
            assert kwargs['AuthParameters']['USERNAME'] == 'test@example.com'
            assert kwargs['AuthParameters']['PASSWORD'] == 'password123'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            'email': 'test@example.com',
            'password': 'wrong-password'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the initiate_auth method to raise ClientError with NotAuthorizedException
            error_response = {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Incorrect username or password'
                }
            }
            mock_client.initiate_auth.side_effect = ClientError(error_response, 'initiate_auth')
            
            # Act
            response = client.post(
                '/api/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert data['message'] == "Invalid email or password"
    
    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # Arrange
        refresh_data = {
            'refresh_token': 'valid-refresh-token'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the initiate_auth response for refresh flow
            mock_client.initiate_auth.return_value = {
                'AuthenticationResult': {
                    'IdToken': 'new-id-token',
                    'AccessToken': 'new-access-token',
                    'ExpiresIn': 3600
                }
            }
            
            # Act
            response = client.post(
                '/api/refresh-token',
                data=json.dumps(refresh_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Token refreshed successfully'
            assert data['tokens']['id_token'] == 'new-id-token'
            assert data['tokens']['access_token'] == 'new-access-token'
            
            # Verify Cognito was called with correct parameters
            mock_client.initiate_auth.assert_called_once()
            _, kwargs = mock_client.initiate_auth.call_args
            assert kwargs['AuthFlow'] == 'REFRESH_TOKEN_AUTH'
            assert kwargs['AuthParameters']['REFRESH_TOKEN'] == 'valid-refresh-token'
    
    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid refresh token."""
        # Arrange
        refresh_data = {
            'refresh_token': 'invalid-refresh-token'
        }
        
        # Mock the Cognito client
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            
            # Mock the initiate_auth method to raise ClientError with NotAuthorizedException
            error_response = {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Invalid refresh token'
                }
            }
            mock_client.initiate_auth.side_effect = ClientError(error_response, 'initiate_auth')
            
            # Act
            response = client.post(
                '/api/refresh-token',
                data=json.dumps(refresh_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert data['message'] == "Invalid or expired refresh token"