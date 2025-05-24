import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

def generate_test_data():
    return {
        "unique_id": random.randint(1, 10**8),
        "username": f"user_{random.randint(1, 10**6)}",
        "statuses": ["available", "pending", "sold"]
    }

# Helper functions
def create_pet():
    data = generate_test_data()
    pet = {
        "id": data["unique_id"],
        "name": "TestPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": random.choice(data["statuses"])
    }
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps(pet),
        headers={'Content-Type': 'application/json'}
    )
    return pet["id"], response

# Pet Endpoints
def test_post_pet_valid():
    pet_id, response = create_pet()
    assert response.status_code == 200
    assert requests.get(f"{BASE_URL}/pet/{pet_id}").status_code == 200

def test_post_pet_invalid():
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps({"name": "Invalid"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]

def test_put_pet_valid():
    pet_id, _ = create_pet()
    update_data = {
        "id": pet_id,
        "name": "Updated",
        "photoUrls": ["http://new.url"],
        "status": "pending"
    }
    response = requests.put(
        f"{BASE_URL}/pet",
        data=json.dumps(update_data),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    assert requests.get(f"{BASE_URL}/pet/{pet_id}").json()["name"] == "Updated"

def test_get_pet_by_status():
    data = generate_test_data()
    for status in data["statuses"]:
        response = requests.get(
            f"{BASE_URL}/pet/findByStatus",
            params={"status": status}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

# Store Endpoints
def test_store_order_flow():
    order_id = generate_test_data()["unique_id"]
    order = {
        "id": order_id,
        "petId": create_pet()[0],
        "quantity": 1,
        "shipDate": "2023-01-01T00:00:00Z",
        "status": "placed",
        "complete": False
    }
    
    # Create
    create_response = requests.post(
        f"{BASE_URL}/store/order",
        data=json.dumps(order),
        headers={'Content-Type': 'application/json'}
    )
    assert create_response.status_code == 200
    
    # Get
    get_response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert get_response.status_code == 200
    
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert delete_response.status_code in [200, 404]

# User Endpoints
def test_user_lifecycle():
    user_data = {
        "username": generate_test_data()["username"],
        "email": "test@example.com",
        "password": "test123"
    }
    
    # Create
    create_response = requests.post(
        f"{BASE_URL}/user",
        data=json.dumps(user_data),
        headers={'Content-Type': 'application/json'}
    )
    assert create_response.status_code == 200
    
    # Login
    login_response = requests.get(
        f"{BASE_URL}/user/login",
        params={"username": user_data["username"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    
    # Update
    update_data = {"email": "new@example.com"}
    update_response = requests.put(
        f"{BASE_URL}/user/{user_data['username']}",
        data=json.dumps(update_data),
        headers={'Content-Type': 'application/json'}
    )
    assert update_response.status_code == 200
    
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert delete_response.status_code == 200

# Auth Tests
def test_protected_operations():
    # Test without auth
    response = requests.delete(f"{BASE_URL}/pet/999")
    assert response.status_code in [401, 404]
    
    # Test with invalid auth
    response = requests.delete(
        f"{BASE_URL}/pet/999",
        headers={"api_key": "invalid"}
    )
    assert response.status_code in [401, 404]
    
    # Test with valid auth
    response = requests.delete(
        f"{BASE_URL}/pet/999",
        headers={"api_key": "special-key"}
    )
    assert response.status_code in [200, 404]

# Error Handling Tests
def test_error_responses():
    # Invalid ID format
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 404
    
    # Non-existent resource
    response = requests.get(f"{BASE_URL}/pet/{generate_test_data()['unique_id']}")
    assert response.status_code == 404
    
    # Missing required fields
    response = requests.post(
        f"{BASE_URL}/user",
        data=json.dumps({"email": "invalid"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]

# Stability Improvements
@pytest.mark.flaky(reruns=3)
def test_eventual_consistency():
    pet_id, _ = create_pet()
    time.sleep(1)  # Wait for propagation
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200