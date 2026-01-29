#!/usr/bin/env python3
"""
Simple API test script
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.json()}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Root endpoint: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!",
        "phone_number": "+1234567890",
        "role": "customer",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"✓ User registration: Status {response.status_code}")
    if response.status_code == 201:
        print(f"  User created: {response.json()['email']}")
        return True
    elif response.status_code == 400:
        print("  User already exists (OK)")
        return True
    return False

def test_login():
    """Test user login"""
    data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    if response.status_code == 200:
        tokens = response.json()
        print(f"✓ Login successful: Got access token")
        return tokens['access_token']
    return None

def test_protected_endpoint(token):
    """Test protected endpoint with token"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✓ Protected endpoint: Accessed as {user['email']}")
        return True
    return False

def test_restaurants():
    """Test restaurant listing"""
    response = requests.get(f"{BASE_URL}/api/restaurants")
    print(f"✓ List restaurants: Status {response.status_code}")
    if response.status_code == 200:
        restaurants = response.json()
        print(f"  Found {len(restaurants)} restaurants")
        return True
    return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Food & Parcel Delivery API")
    print("=" * 50)

    tests_passed = 0
    tests_total = 0

    # Test 1: Health check
    tests_total += 1
    if test_health():
        tests_passed += 1
    print()

    # Test 2: Root endpoint
    tests_total += 1
    if test_root():
        tests_passed += 1
    print()

    # Test 3: User registration
    tests_total += 1
    if test_register():
        tests_passed += 1
    print()

    # Test 4: User login
    tests_total += 1
    token = test_login()
    if token:
        tests_passed += 1
    print()

    # Test 5: Protected endpoint
    if token:
        tests_total += 1
        if test_protected_endpoint(token):
            tests_passed += 1
        print()

    # Test 6: List restaurants
    tests_total += 1
    if test_restaurants():
        tests_passed += 1
    print()

    # Summary
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("=" * 50)

    if tests_passed == tests_total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
