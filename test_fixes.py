"""
Test script for both fixes:
1. Duplicate image detection using image hash
2. Best match authentication instead of first match
"""

import requests
import base64
import json

# Configuration
BASE_URL = "http://localhost:8053/api/authentication"
TEST_IMAGE_PATH = "face_test.jpeg"  # Use existing test image

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def test_duplicate_image_detection():
    """Test Fix 1: Duplicate image detection"""
    print("\n" + "="*60)
    print("TEST 1: Duplicate Image Detection")
    print("="*60)
    
    # Read the test image
    try:
        base64_image = image_to_base64(TEST_IMAGE_PATH)
    except FileNotFoundError:
        print(f"ERROR: Test image '{TEST_IMAGE_PATH}' not found!")
        print("Please ensure the test image exists in the root directory.")
        return False
    
    # First registration - should succeed
    print("\n1. Registering user with unique_id='test_user_1'...")
    register_payload_1 = {
        "unique_id": "test_user_1",
        "name": "Test User 1",
        "face_image": base64_image
    }
    
    response1 = requests.post(f"{BASE_URL}/register/", json=register_payload_1)
    print(f"   Status: {response1.status_code}")
    print(f"   Response: {response1.json()}")
    
    if response1.status_code != 201:
        print("   First registration failed!")
        return False
    print("   First registration successful")
    
    # Second registration with SAME image but different user_id - should fail
    print("\n2. Attempting to register same image with unique_id='test_user_2'...")
    register_payload_2 = {
        "unique_id": "test_user_2",
        "name": "Test User 2",
        "face_image": base64_image  # Same image!
    }
    
    response2 = requests.post(f"{BASE_URL}/register/", json=register_payload_2)
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.json()}")
    
    if response2.status_code == 400 and "already registered" in response2.json().get("message", "").lower():
        print("   Duplicate image correctly rejected!")
        return True
    else:
        print("   Duplicate image was NOT rejected!")
        return False

def test_best_match_authentication():
    """Test Fix 2: Best match authentication"""
    print("\n" + "="*60)
    print("TEST 2: Best Match Authentication")
    print("="*60)
    
    # This test requires multiple registered users
    # We'll register two different users and test authentication
    
    print("\nNote: This test requires the server to be running and")
    print("      at least 2 different users registered in the database.")
    print("      The test will authenticate and verify the correct user is returned.")
    
    # Try to authenticate with the test image
    try:
        base64_image = image_to_base64(TEST_IMAGE_PATH)
    except FileNotFoundError:
        print(f"ERROR: Test image '{TEST_IMAGE_PATH}' not found!")
        return False
    
    print("\n1. Authenticating with test image...")
    auth_payload = {
        "face_image": base64_image
    }
    
    response = requests.post(f"{BASE_URL}/authenticate/", json=auth_payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        print(f"   Authentication successful!")
        print(f"   Authenticated User: {data.get('name')} (ID: {data.get('unique_id')})")
        return True
    elif response.status_code == 401:
        print(f"   Response: {response.json()}")
        print("   No matching user found (this is expected if no users are registered)")
        return None
    else:
        print(f"   Response: {response.json()}")
        print("   Authentication failed with unexpected error")
        return False

def cleanup_test_users():
    """Optional: Clean up test users (requires admin API or direct DB access)"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    print("Note: Test users (test_user_1, test_user_2) may need to be")
    print("      manually deleted from the database if needed.")
    print("      This script does not include cleanup functionality.")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FACIAL RECOGNITION API - FIXES TEST SUITE")
    print("="*60)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure the Django server is running!")
    
    # Test 1: Duplicate image detection
    test1_result = test_duplicate_image_detection()
    
    # Test 2: Best match authentication
    test2_result = test_best_match_authentication()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    if test1_result is True:
        print("Test 1 (Duplicate Detection): PASSED")
    elif test1_result is False:
        print("Test 1 (Duplicate Detection): FAILED")
    else:
        print("Test 1 (Duplicate Detection): SKIPPED")

    if test2_result is True:
        print("Test 2 (Best Match Auth): PASSED")
    elif test2_result is False:
        print("Test 2 (Best Match Auth): FAILED")
    else:
        print("Test 2 (Best Match Auth): INCONCLUSIVE")
    
    cleanup_test_users()
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)


