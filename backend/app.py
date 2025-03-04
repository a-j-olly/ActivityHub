from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
import json
from decimal import Decimal
from flask.json.provider import JSONProvider
from config import config_by_name
from utils.errors import register_error_handlers
from routes.auth import auth_bp
from routes.users import users_bp

# Custom JSON Provider to handle Decimal values
class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, default=self._default)
    
    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    
    def _default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def create_app(config_name='default'):
    """
    Create and configure a Flask application instance.
    
    Args:
        config_name (str, optional): The configuration environment to use.
                                     One of 'development', 'testing', 'production', 'default'.
                                     Defaults to 'default'.
    
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration based on config_name
    app.config.from_object(config_by_name[config_name])
    
    # Register custom JSON provider
    app.json = CustomJSONProvider(app)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to ActivityHub API',
            'status': 'success',
            'version': '1.0.0'
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy'
        })
    
    return app

# Create the application instance
if __name__ == '__main__':
    # Determine which configuration to use based on environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(debug=app.config['DEBUG'], host='0.0.0.0')