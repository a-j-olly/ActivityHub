import pytest
import json
from app import create_app

class TestApp:
    def test_app_creation(self):
        """Test application factory creates a Flask app."""
        # Act
        app = create_app()
        
        # Assert
        assert app is not None
        assert app.name == 'app'
    
    def test_config_loading(self):
        """Test application loads different configurations."""
        # Act - Test development config
        dev_app = create_app('development')
        
        # Assert
        assert dev_app.config['DEBUG'] is True
        
        # Act - Test production config
        prod_app = create_app('production')
        
        # Assert
        assert prod_app.config['DEBUG'] is False
        
        # Act - Test testing config
        test_app = create_app('testing')
        
        # Assert
        assert test_app.config['TESTING'] is True
    
    def test_index_route(self, client):
        """Test the index route returns welcome message."""
        # Act
        response = client.get('/')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Welcome to ActivityHub API'
        assert data['status'] == 'success'
    
    def test_health_check_route(self, client):
        """Test the health check endpoint."""
        # Act
        response = client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_404_error_handler(self, client):
        """Test 404 error handler for nonexistent routes."""
        # Act
        response = client.get('/nonexistent-route')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'NOT_FOUND'
        assert 'message' in data
        assert data['statusCode'] == 404
    
    def test_method_not_allowed_handler(self, client):
        """Test handling of methods not allowed."""
        # Act - POST to the index route which only supports GET
        response = client.post('/')
        
        # Assert
        assert response.status_code == 405  # Method Not Allowed
    
    def test_custom_json_provider(self, app):
        """Test custom JSON provider handles Decimal values."""
        # We would need to test this with a route that returns Decimal values
        # For now, just verify app has a custom json provider configured
        assert hasattr(app, 'json')
        
        # In a real test, we would make a request that returns Decimal values
        # and verify they are properly converted to floats in the response
