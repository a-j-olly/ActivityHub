#!/usr/bin/env python
"""
This script tests the DynamoDB integration by creating a test user and retrieving it.
"""

import boto3
import time
import os
import sys
import json
import uuid
import requests

# Add parent directory to path to import from config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API base URL
API_BASE_URL = 'http://localhost:5000/api'

def test_register_endpoint():
    """Test the register endpoint"""
    print("\n--- Testing /register endpoint ---")
    
    # Create a test user with a unique email
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"test.user+{unique_id}@example.com"
    
    user_data = {
        'email': test_email,
        'name': f"Test User {unique_id}",
        'password': 'password123',
        'role': 'parent'
    }
    
    # Send request to register endpoint
    response = requests.post(f"{API_BASE_URL}/register", json=user_data)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Register endpoint test passed!")
        return response.json()['user']['user_id']
    else:
        print("❌ Register endpoint test failed!")
        return None

def test_login_endpoint(email, password):
    """Test the login endpoint"""
    print("\n--- Testing /login endpoint ---")
    
    login_data = {
        'email': email,
        'password': password
    }
    
    # Send request to login endpoint
    response = requests.post(f"{API_BASE_URL}/login", json=login_data)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login endpoint test passed!")
        return response.json()['token']
    else:
        print("❌ Login endpoint test failed!")
        return None

def test_get_user_endpoint(user_id, token):
    """Test the get user endpoint"""
    print(f"\n--- Testing /users/{user_id} endpoint ---")
    
    # Send request to get user endpoint
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/users/{user_id}", headers=headers)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user endpoint test passed!")
    else:
        print("❌ Get user endpoint test failed!")

def test_update_user_endpoint(user_id, token):
    """Test the update user endpoint"""
    print(f"\n--- Testing /users/{user_id} PUT endpoint ---")
    
    update_data = {
        'name': f"Updated User Name {uuid.uuid4().hex[:4]}"
    }
    
    # Send request to update user endpoint
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.put(f"{API_BASE_URL}/users/{user_id}", json=update_data, headers=headers)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Update user endpoint test passed!")
    else:
        print("❌ Update user endpoint test failed!")

def main():
    """Run the test script"""
    print("Testing DynamoDB integration with Flask API...")
    
    # Test register endpoint
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"test.user+{unique_id}@example.com"
    test_password = "password123"
    
    user_data = {
        'email': test_email,
        'name': f"Test User {unique_id}",
        'password': test_password,
        'role': 'parent'
    }
    
    # Test register endpoint
    print("\n--- Testing /register endpoint ---")
    response = requests.post(f"{API_BASE_URL}/register", json=user_data)
    
    # Print response
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Register endpoint test passed!")
        user_id = response.json()['user']['user_id']
        print(f"Created user with ID: {user_id}")
    else:
        print("❌ Register endpoint test failed!")
        print(f"Response: {response.text}")
        return
    
    # Test login endpoint
    print("\n--- Testing /login endpoint ---")
    login_data = {
        'email': test_email,
        'password': test_password
    }
    
    response = requests.post(f"{API_BASE_URL}/login", json=login_data)
    
    # Print response
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login endpoint test passed!")
        token = response.json()['token']
    else:
        print("❌ Login endpoint test failed!")
        print(f"Response: {response.text}")
        return
    
    # Test get user endpoint
    test_get_user_endpoint(user_id, token)
    
    # Test update user endpoint
    test_update_user_endpoint(user_id, token)
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    main()
