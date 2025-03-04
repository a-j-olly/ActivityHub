from flask import jsonify, current_app

def error_response(error_type, message=None, status_code=None):
    """
    Creates a standardized error response
    
    Args:
        error_type (str): Type of error (e.g., 'BAD_REQUEST', 'UNAUTHORIZED')
        message (str, optional): Custom error message. Defaults to None.
        status_code (int, optional): HTTP status code. Defaults to None.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    error_types = {
        'BAD_REQUEST': 400,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'NOT_FOUND': 404,
        'SERVER_ERROR': 500
    }
    
    # Get status code from error type if not provided
    if status_code is None:
        status_code = error_types.get(error_type, 500)
    
    # Get message from Flask app config if not provided
    if message is None:
        # Get the error messages from current app's config
        error_messages = current_app.config.get('ERROR_MESSAGES', {})
        message = error_messages.get(error_type, 'An error occurred')
    
    response = {
        'error': error_type,
        'message': message,
        'statusCode': status_code
    }
    
    return jsonify(response), status_code

def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(e):
        return error_response('BAD_REQUEST')
    
    @app.errorhandler(401)
    def unauthorized(e):
        return error_response('UNAUTHORIZED')
    
    @app.errorhandler(403)
    def forbidden(e):
        return error_response('FORBIDDEN')
    
    @app.errorhandler(404)
    def not_found(e):
        return error_response('NOT_FOUND')
    
    @app.errorhandler(500)
    def server_error(e):
        return error_response('SERVER_ERROR')
