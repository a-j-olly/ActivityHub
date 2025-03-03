from flask import Flask, jsonify
from flask_cors import CORS
from decimal import Decimal
import logging
import json

# Import error handlers and routes
from utils.errors import register_error_handlers
from routes.auth import auth_bp

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def create_app(config_object='config'):
    """
    Create and configure a Flask application instance
    
    Args:
        config_object (str, optional): The configuration object to use. Defaults to 'config'.
    
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_object)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Configure JSON encoder to handle Decimal objects
    app.json_encoder = CustomJSONEncoder
    
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
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0')