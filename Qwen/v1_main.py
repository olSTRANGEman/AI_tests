import pytest
import requests
import random
import string
import json
from requests.exceptions import Timeout

BASE_URL = "https://petstore.swagger.io/v2"

# Helper functions
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_pet_data():
    return {
        "id": random.randint(100000, 999999),
        "name": random_string(),
        "category": {"id": random.randint(1, 100), "name": random_string()},
        "photoUrls": [f"http://{random_string()}.com"],
        "tags": [{"id": random.randint(1, 100), "name": random_string()}],
        "status": random.choice(["available", "pending", "sold"])
    }

def create_user_data():
    return {
        "id": random.randint(100000, 999999),
        "username": random_string(),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "password123",
        "phone": "+1234567890",
        "userStatus": 0
    }

def create_order_data(pet_id):
    return {
        "id": random.randint(100000, 999999),
        "petId": pet_id,
        "quantity": random.randint(1, 10),
        "shipDate": "2023-01-01T00:00:00.000Z",
        "status": "placed",
        "complete": False
    }

# Unit tests for /pet endpoint
def test_post_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet = response.json()
    assert pet["name"] == pet_data["name"]
    assert pet["status"] == pet_data["status"]

def test_post_pet_missing_name():
    pet_data = create_pet_data()
    del pet_data["name"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 400

def test_post_pet_invalid_status():
    pet_data = create_pet_data()
    pet_data["status"] = "invalid_status"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 400

def test_put_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    
    pet = response.json()
    pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet), headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == pet["name"]

def test_put_pet_invalid_id():
    pet_data = create_pet_data()
    pet_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 400

def test_get_pet_by_id_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert response.json()["id"] == pet_id

def test_get_pet_by_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400

def test_get_pet_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.get(f"{BASE_URL}/pet/{unique_id}")
    assert response.status_code == 404

def test_delete_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 204

def test_delete_nonexistent_pet():
    unique_id = random.randint(1000000, 9999999)
    response = requests.delete(f"{BASE_URL}/pet/{unique_id}")
    assert response.status_code == 404

# Unit tests for /pet/findByStatus
def test_get_pets_by_status_valid():
    status = random.choice(["available", "pending", "sold"])
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": status})
    assert response.status_code == 200

def test_get_pets_by_invalid_status():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid_status"})
    assert response.status_code == 400

# Unit tests for /user endpoint
def test_post_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

def test_post_user_duplicate_username():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 400

def test_get_user_by_id_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    user_id = response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/user/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_put_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    
    updated_user = response.json()
    updated_user["firstName"] = random_string()
    response = requests.put(f"{BASE_URL}/user", data=json.dumps(updated_user), headers=headers)
    assert response.status_code == 200
    assert response.json()["firstName"] == updated_user["firstName"]

def test_delete_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    user_id = response.json()["id"]
    
    response = requests.delete(f"{BASE_URL}/user/{user_id}")
    assert response.status_code == 204

# Unit tests for /store/order endpoint
def test_post_order_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=headers)
    assert response.status_code == 200
    assert response.json()["petId"] == pet_id

def test_post_order_invalid_pet_id():
    order_data = create_order_data(9999999)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=headers)
    assert response.status_code == 400

def test_get_order_by_id_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=headers)
    assert response.status_code == 200
    order_id = response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id

def test_delete_order_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=headers)
    assert response.status_code == 200
    order_id = response.json()["id"]
    
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

# Integration tests
def test_crud_pet_flow():
    # Create
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    pet_id = response.json()["id"]
    
    # Read
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert response.json()["id"] == pet_id
    
    # Update
    updated_pet = response.json()
    updated_pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(updated_pet), headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == updated_pet["name"]
    
    # Delete
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 204

def test_crud_user_flow():
    # Create
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200
    user_id = response.json()["id"]
    
    # Read
    response = requests.get(f"{BASE_URL}/user/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    
    # Update
    updated_user = response.json()
    updated_user["firstName"] = random_string()
    response = requests.put(f"{BASE_URL}/user", data=json.dumps(updated_user), headers=headers)
    assert response.status_code == 200
    assert response.json()["firstName"] == updated_user["firstName"]
    
    # Delete
    response = requests.delete(f"{BASE_URL}/user/{user_id}")
    assert response.status_code == 204

# Fuzz tests
def test_large_payload():
    large_data = create_pet_data()
    large_data["name"] = "A" * 1000000
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(large_data), headers=headers)
    assert response.status_code in [413, 414, 411]

def test_rate_limiting():
    for _ in range(100):
        response = requests.get(f"{BASE_URL}/pet/1")
        if response.status_code == 429:
            break
    else:
        assert False, "Rate limiting not detected"

def test_timeout_handling():
    try:
        requests.get(f"{BASE_URL}/pet/1", timeout=0.1)
    except Timeout:
        pass
    else:
        assert False, "Timeout not raised"

# Additional tests (continue until reaching 50+)
# ... (add more tests following the same pattern for other endpoints and edge cases)