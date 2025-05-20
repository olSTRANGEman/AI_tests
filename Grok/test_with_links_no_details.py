import pytest
import requests
import json
import time
import uuid
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Base URL for the Petstore API
BASE_URL = "https://petstore.swagger.io/v2"

# Helper function to generate unique IDs
def generate_unique_id():
    return str(uuid.uuid4()).replace("-", "")[:10]

# Helper function to generate unique pet data
def generate_pet_data():
    unique_id = generate_unique_id()
    return {
        "id": int(time.time() * 1000),
        "name": f"Pet_{unique_id}",
        "status": "available",
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["string"],
        "tags": [{"id": 1, "name": "tag1"}]
    }

# Helper function to generate unique order data
def generate_order_data(pet_id):
    unique_id = generate_unique_id()
    return {
        "id": int(time.time() * 1000),
        "petId": pet_id,
        "quantity": 1,
        "shipDate": "2025-05-20T18:00:00.000Z",
        "status": "placed",
        "complete": True
    }

# Helper function to generate unique user data
def generate_user_data():
    unique_id = generate_unique_id()
    return {
        "id": int(time.time() * 1000),
        "username": f"user_{unique_id}",
        "firstName": "John",
        "lastName": "Doe",
        "email": f"user_{unique_id}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }

# Schema for pet response
PET_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "photoUrls"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "status": {"type": "string"},
        "category": {"type": ["object", "null"], "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
        "photoUrls": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}}
    }
}

# Schema for order response
ORDER_SCHEMA = {
    "type": "object",
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"],
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"}
    }
}

# Schema for user response
USER_SCHEMA = {
    "type": "object",
    "required": ["id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"],
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"}
    }
}

# Unit Tests for /pet
def test_post_pet_valid():
    pet_data = generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_post_pet_invalid_id():
    pet_data = generate_pet_data()
    pet_data["id"] = "invalid"
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 400

def test_post_pet_missing_name():
    pet_data = generate_pet_data()
    del pet_data["name"]
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 400

def test_post_pet_invalid_method():
    response = requests.get(f"{BASE_URL}/pet")
    assert response.status_code == 405

def test_put_pet_valid():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_data["name"] = "Updated_Pet"
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_put_pet_invalid_id():
    pet_data = generate_pet_data()
    pet_data["id"] = "invalid"
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 400

def test_put_pet_not_found():
    pet_data = generate_pet_data()
    pet_data["id"] = 999999999
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 404

def test_put_pet_invalid_method():
    response = requests.delete(f"{BASE_URL}/pet")
    assert response.status_code == 405

def test_get_pet_by_status_valid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available")
    assert response.status_code == 200
    for pet in response.json():
        validate(instance=pet, schema=PET_SCHEMA)

def test_get_pet_by_status_missing():
    response = requests.get(f"{BASE_URL}/pet/findByStatus")
    assert response.status_code == 400

# Unit Tests for /pet/{petId}
def test_get_pet_by_id_valid():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_get_pet_by_id_invalid():
    response = requests.get(f"{BASE_URL}/pet/invalid")
    assert response.status_code == 404

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

def test_post_pet_by_id_valid():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", data={"name": "Updated_Name", "status": "sold"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200

def test_post_pet_by_id_invalid():
    response = requests.post(f"{BASE_URL}/pet/invalid", data={"name": "Updated_Name", "status": "sold"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 404

def test_post_pet_by_id_invalid_method():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    response = requests.put(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 405

def test_delete_pet_valid():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

def test_delete_pet_invalid_id():
    response = requests.delete(f"{BASE_URL}/pet/invalid")
    assert response.status_code == 404

def test_delete_pet_not_found():
    response = requests.delete(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

# Unit Tests for /store/inventory
def test_get_store_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# Unit Tests for /store/order
def test_post_store_order_valid():
    pet_data = generate_pet_data()
    create_pet = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_pet.status_code == 200
    order_data = generate_order_data(pet_data["id"])
    response = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_post_store_order_invalid_pet():
    order_data = generate_order_data(999999999)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert response.status_code == 400

def test_post_store_order_missing_fields():
    order_data = generate_order_data(1000)
    del order_data["petId"]
    response = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert response.status_code == 400

def test_get_store_order_valid():
    pet_data = generate_pet_data()
    create_pet = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_pet.status_code == 200
    order_data = generate_order_data(pet_data["id"])
    create_order = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert create_order.status_code == 200
    order_id = order_data["id"]
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_get_store_order_invalid():
    response = requests.get(f"{BASE_URL}/store/order/invalid")
    assert response.status_code == 404

def test_get_store_order_not_found():
    response = requests.get(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_delete_store_order_valid():
    pet_data = generate_pet_data()
    create_pet = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_pet.status_code == 200
    order_data = generate_order_data(pet_data["id"])
    create_order = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert create_order.status_code == 200
    order_id = order_data["id"]
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_store_order_invalid():
    response = requests.delete(f"{BASE_URL}/store/order/invalid")
    assert response.status_code == 404

def test_delete_store_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

# Unit Tests for /user
def test_post_user_valid():
    user_data = generate_user_data()
    response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert response.status_code == 200

def test_post_user_invalid_email():
    user_data = generate_user_data()
    user_data["email"] = "invalid"
    response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert response.status_code == 400

def test_post_user_missing_username():
    user_data = generate_user_data()
    del user_data["username"]
    response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert response.status_code == 400

def test_get_user_valid():
    user_data = generate_user_data()
    create_user = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_user.status_code == 200
    username = user_data["username"]
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)

def test_get_user_invalid():
    response = requests.get(f"{BASE_URL}/user/invalid%20username")
    assert response.status_code == 404

def test_get_user_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_put_user_valid():
    user_data = generate_user_data()
    create_user = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_user.status_code == 200
    username = user_data["username"]
    user_data["firstName"] = "Updated_Name"
    response = requests.put(f"{BASE_URL}/user/{username}", json=user_data)
    assert response.status_code == 200

def test_put_user_not_found():
    user_data = generate_user_data()
    response = requests.put(f"{BASE_URL}/user/nonexistent_user", json=user_data)
    assert response.status_code == 404

def test_put_user_invalid_data():
    user_data = generate_user_data()
    create_user = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_user.status_code == 200
    username = user_data["username"]
    user_data["email"] = "invalid"
    response = requests.put(f"{BASE_URL}/user/{username}", json=user_data)
    assert response.status_code == 400

def test_delete_user_valid():
    user_data = generate_user_data()
    create_user = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_user.status_code == 200
    username = user_data["username"]
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_delete_user_invalid():
    response = requests.delete(f"{BASE_URL}/user/invalid%20username")
    assert response.status_code == 404

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_user_login_valid():
    user_data = generate_user_data()
    create_user = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_user.status_code == 200
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert response.status_code == 200
    assert "X-Rate-Limit" in response.headers

def test_user_login_missing_params():
    response = requests.get(f"{BASE_URL}/user/login")
    assert response.status_code == 400

def test_user_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

# Integration Tests
def test_crud_pet_flow():
    pet_data = generate_pet_data()
    # Create
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    # Read
    read_response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert read_response.status_code == 200
    validate(instance=read_response.json(), schema=PET_SCHEMA)
    # Update
    pet_data["name"] = "Updated_Pet"
    update_response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    assert update_response.status_code == 200
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert delete_response.status_code == 200

def test_crud_store_order_flow():
    pet_data = generate_pet_data()
    create_pet = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_pet.status_code == 200
    # Create
    order_data = generate_order_data(pet_data["id"])
    create_response = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert create_response.status_code == 200
    order_id = order_data["id"]
    # Read
    read_response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert read_response.status_code == 200
    validate(instance=read_response.json(), schema=ORDER_SCHEMA)
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert delete_response.status_code == 200

def test_crud_user_flow():
    user_data = generate_user_data()
    # Create
    create_response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_response.status_code == 200
    username = user_data["username"]
    # Read
    read_response = requests.get(f"{BASE_URL}/user/{username}")
    assert read_response.status_code == 200
    validate(instance=read_response.json(), schema=USER_SCHEMA)
    # Update
    user_data["firstName"] = "Updated_Name"
    update_response = requests.put(f"{BASE_URL}/user/{username}", json=user_data)
    assert update_response.status_code == 200
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/user/{username}")
    assert delete_response.status_code == 200

def test_auth_and_access_flow():
    user_data = generate_user_data()
    # Create
    create_response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert create_response.status_code == 200
    # Login
    login_response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert login_response.status_code == 200
    # Invalid login
    invalid_login = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password=wrong")
    assert invalid_login.status_code == 200  # API returns 200 with error message

# Fault Tolerance and Load Tests
def test_post_pet_rate_limit():
    for _ in range(10):
        pet_data = generate_pet_data()
        response = requests.post(f"{BASE_URL}/pet", json=pet_data)
        if response.status_code == 429:
            break
    else:
        pytest.fail("No rate limit detected after 10 rapid requests")

def test_post_pet_large_payload():
    pet_data = generate_pet_data()
    pet_data["name"] = "x" * 1000000
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code in [400, 413, 500]

def test_timeout_get_pet():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    pet_id = pet_data["id"]
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/pet/{pet_id}", timeout=0.001)

def test_post_user_rate_limit():
    for _ in range(10):
        user_data = generate_user_data()
        response = requests.post(f"{BASE_URL}/user", json=user_data)
        if response.status_code == 429:
            break
    else:
        pytest.fail("No rate limit detected after 10 rapid requests")

def test_post_user_large_payload():
    user_data = generate_user_data()
    user_data["username"] = "x" * 1000000
    response = requests.post(f"{BASE_URL}/user", json=user_data)
    assert response.status_code in [400, 413, 500]

def test_timeout_store_inventory():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/store/inventory", timeout=0.001)

def test_invalid_json_post_pet():
    response = requests.post(f"{BASE_URL}/pet", data="invalid_json", headers={"Content-Type": "application/json"})
    assert response.status_code == 400

def test_duplicate_pet_id():
    pet_data = generate_pet_data()
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert create_response.status_code == 200
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code in [400, 409]