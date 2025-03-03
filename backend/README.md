# ActivityHub Backend API

This directory contains the Flask API backend for the ActivityHub application.

## Project Structure

```
backend/
├── app.py                # Main application entry point
├── config.py             # Configuration settings
├── routes/               # API route handlers
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   └── ...               # Other route modules
├── models/               # Data models
│   ├── __init__.py
│   ├── user.py           # User model
│   └── ...               # Other model modules
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── auth.py           # Authentication utilities
│   ├── database.py       # Database utility functions
│   └── errors.py         # Error handling utilities
└── requirements.txt      # Project dependencies
```

## Setup and Installation

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (optional):
   ```bash
   # On Windows
   set FLASK_ENV=development
   set FLASK_APP=app.py
   
   # On macOS/Linux
   export FLASK_ENV=development
   export FLASK_APP=app.py
   ```

4. Run the application:
   ```bash
   # Using Flask CLI
   flask run
   
   # Or directly
   python app.py
   ```

## API Endpoints

### Authentication

#### Register a new user
- **URL**: `/api/register`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "name": "Full Name",
    "password": "securepassword",
    "role": "parent",  // Optional, defaults to "child"
    "parent_id": "uuid" // Required for child users
  }
  ```
- **Response**: 
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "Full Name",
      "role": "parent",
      "created_at": 1645123456
    }
  }
  ```

#### Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**: 
  ```json
  {
    "message": "Login successful",
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "Full Name",
      "role": "parent",
      "created_at": 1645123456
    },
    "token": "jwt-token"
  }
  ```

## Error Handling

The API returns standardized error responses in the following format:

```json
{
  "error": "ERROR_TYPE",
  "message": "Descriptive error message",
  "statusCode": 400
}
```

Common error types:
- `BAD_REQUEST` (400): Invalid request data
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `SERVER_ERROR` (500): Internal server error

## Authentication and Authorization

The API uses JWT tokens for authentication. Protected endpoints require a valid token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

Different endpoints may require specific roles (child, parent, or admin) to access.