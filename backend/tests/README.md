# ActivityHub Backend Tests

This directory contains tests for the ActivityHub Flask API backend. The tests are written using pytest and follow Flask 2.3.x testing best practices.

## Test Structure

The tests are organized into several categories:

- **Unit Tests**: Test individual components in isolation
  - `test_auth_utils.py`: Tests for authentication utility functions
  - `test_database_utils.py`: Tests for database utility functions
  - `test_error_utils.py`: Tests for error handling utilities
  - `test_user_model.py`: Tests for the User model class

- **API Tests**: Test the API endpoints
  - `test_auth_routes.py`: Tests for authentication endpoints
  - `test_user_routes.py`: Tests for user management endpoints
  
- **Application Tests**: Test the overall application
  - `test_app.py`: Tests for application creation and configuration

## Test Setup

Tests use fixtures defined in `conftest.py` to set up the test environment, including:

- Flask application with test configuration
- Test client for making requests
- Mocked DynamoDB to avoid hitting real AWS services
- Test users with different roles
- Authentication helpers

## Running Tests

### Running All Tests

```bash
cd backend
python -m pytest
```

### Running Specific Test Categories

```bash
# Run only authentication-related tests
python -m pytest -m auth

# Run only model tests
python -m pytest -m model

# Run only tests for API endpoints
python -m pytest -m api
```

### Running With Coverage Report

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Mocking Strategy

The tests use a mocking strategy to avoid making real AWS API calls:

- **DynamoDB**: A dictionary-based mock that simulates DynamoDB operations
- **Authentication**: All JWT generation/validation is done with real implementations but using test keys

## Test Fixtures

Key fixtures include:

- `app`: A Flask application configured for testing
- `client`: A test client for making HTTP requests
- `mock_db`: A mock DynamoDB implementation
- `auth_headers`: Helper to generate authentication headers
- `test_user`: A pre-configured parent user
- `test_child_user`: A pre-configured child user linked to the parent

## Best Practices Followed

1. **Using pytest fixtures** for clean, reusable test setups
2. **Properly mocking external dependencies** to ensure tests are fast and reliable
3. **Testing both success and error cases** for full coverage
4. **Following AAA pattern** (Arrange-Act-Assert) for clear test structure
5. **Using parameterized tests** where appropriate for testing similar scenarios
6. **Isolating tests** so they don't interfere with each other
7. **Testing edge cases** and boundary conditions
8. **Including docstrings** to explain the purpose of each test

## Adding New Tests

When adding new tests:

1. Consider whether your test fits into an existing file or needs a new one
2. Use the existing fixtures where possible
3. Follow the AAA (Arrange-Act-Assert) pattern
4. Add appropriate markers to categorize your test
5. Ensure your test doesn't depend on external services
6. Add docstrings explaining what your test is checking
