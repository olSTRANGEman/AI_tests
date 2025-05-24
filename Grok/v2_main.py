import pytest
import requests
import time
import random
import string
import json

BASE_URL = "https://petstore.swagger.io/v2"
API_KEY = "special-key"  # As per specification example
TIMEOUT = 5

# Helper function to generate random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Helper function to generate random pet data
def generate_pet_data():
    return {
        "id": random.randint(1000, 9999),
        "name": random_string(),
        "category": {"id": 1, "name": "test_category"},
        "photoUrls": ["http://test.com"],
        "tags": [{"id": 1, "name": "test_tag"}],
        "status": "available"
    }

# Helper function to generate user data
def generate_user_data():
    return {
        "id": random.randint(1000, 9999),
        "username": random_string(),
        "firstName": "Test",
        "lastName": "User",
        "email": f"{random_string()}@test.com",
        "password": random_string(),
        "phone": "1234567890",
        "userStatus": 1
    }

# --- /pet Endpoint Tests ---

def test_post_pet_valid():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["name"] == pet_data["name"]
    assert response.json()["id"] == pet_data["id"]

def test_post_pet_invalid_data():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", json={"id": "invalid"}, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 400

def test_post_pet_missing_api_key():
    pet_data = generate_pet_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 401

def test_get_pet_by_id_valid():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    pet_id = post_response.json()["id"]
    response = requests.get(f"{BASE_URL}/pet/{pet_id}", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["id"] == pet_id

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999", timeout=TIMEOUT)
    assert response.status_code == 404

def test_get_pet_by_id_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/invalid", timeout=TIMEOUT)
    assert response.status_code == 404  # Specification indicates 404 for invalid ID

def test_put_pet_valid():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    pet_id = post_response.json()["id"]
    updated_data = pet_data.copy()
    updated_data["name"] = "updated_" + pet_data["name"]
    response = requests.put(f"{BASE_URL}/pet", json=updated_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]

def test_put_pet_invalid_data():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.put(f"{BASE_URL}/pet", json={"id": "invalid"}, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 400

def test_put_pet_missing_api_key():
    pet_data = generate_pet_data()
    headers = {"Content-Type": "application/json"}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 401

def test_delete_pet_valid():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    pet_id = post_response.json()["id"]
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200

def test_delete_pet_not_found():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/pet/999999", headers=headers, timeout=TIMEOUT)
    assert response.status_code == 404

def test_delete_pet_invalid_id():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/pet/invalid", headers=headers, timeout=TIMEOUT)
    assert response.status_code == 404  # Specification indicates 404 for invalid ID

def test_get_pet_find_by_status_valid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available", timeout=TIMEOUT)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid", timeout=TIMEOUT)
    assert response.status_code == 200  # API returns 200 with empty list for invalid status

def test_get_pet_find_by_tags_valid():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=test_tag", timeout=TIMEOUT)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_tags_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=", timeout=TIMEOUT)
    assert response.status_code == 200  # API returns 200 with empty list for empty tags

def test_post_pet_upload_image_valid():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    pet_id = post_response.json()["id"]
    files = {"file": ("test.txt", b"test content")}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files, headers={"api_key": API_KEY}, timeout=TIMEOUT)
    assert response.status_code == 200

def test_post_pet_upload_image_invalid_id():
    headers = {"api_key": API_KEY}
    files = {"file": ("test.txt", b"test content")}
    response = requests.post(f"{BASE_URL}/pet/invalid/uploadImage", files=files, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 404  # Specification indicates 404 for invalid ID

# --- /store Endpoint Tests ---

def test_get_store_inventory():
    headers = {"api_key": API_KEY}
    response = requests.get(f"{BASE_URL}/store/inventory", headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_post_store_order_valid():
    order_data = {
        "id": random.randint(1000, 9999),
        "petId": random.randint(1000, 9999),
        "quantity": 1,
        "shipDate": "2025-05-24T15:00:00.000Z",
        "status": "placed",
        "complete": False
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["id"] == order_data["id"]

def test_post_store_order_invalid_data():
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/store/order", json={"id": "invalid"}, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 400

def test_get_store_order_by_id_valid():
    order_data = {
        "id": random.randint(1000, 9999),
        "petId": random.randint(1000, 9999),
        "quantity": 1,
        "shipDate": "2025-05-24T15:00:00.000Z",
        "status": "placed",
        "complete": False
    }
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    order_id = post_response.json()["id"]
    response = requests.get(f"{BASE_URL}/store/order/{order_id}", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["id"] == order_id

def test_get_store_order_by_id_not_found():
    response = requests.get(f"{BASE_URL}/store/order/999999", timeout=TIMEOUT)
    assert response.status_code == 404

def test_get_store_order_by_id_invalid_id():
    response = requests.get(f"{BASE_URL}/store/order/invalid", timeout=TIMEOUT)
    assert response.status_code == 404  # Specification indicates 404 for invalid ID

def test_delete_store_order_valid():
    order_data = {
        "id": random.randint(1000, 9999),
        "petId": random.randint(1000, 9999),
        "quantity": 1,
        "shipDate": "2025-05-24T15:00:00.000Z",
        "status": "placed",
        "complete": False
    }
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    order_id = post_response.json()["id"]
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}", timeout=TIMEOUT)
    assert response.status_code == 200

def test_delete_store_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/999999", timeout=TIMEOUT)
    assert response.status_code == 404

def test_delete_store_order_invalid_id():
    response = requests.delete(f"{BASE_URL}/store/order/invalid", timeout=TIMEOUT)
    assert response.status_code == 404  # Specification indicates 404 for invalid ID

# --- /user Endpoint Tests ---

def test_post_user_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200

def test_post_user_invalid_data():
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", json={"id": "invalid"}, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 400

def test_get_user_by_name_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

def test_get_user_by_name_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent", timeout=TIMEOUT)
    assert response.status_code == 404

def test_put_user_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    updated_data = user_data.copy()
    updated_data["firstName"] = "Updated"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", json=updated_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200

def test_put_user_not_found():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.put(f"{BASE_URL}/user/nonexistent", json=user_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 404

def test_delete_user_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}", timeout=TIMEOUT)
    assert response.status_code == 200

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent", timeout=TIMEOUT)
    assert response.status_code == 404

def test_post_create_with_array_valid():
    user_data = [
        generate_user_data(),
        generate_user_data()
    ]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=user_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200

def test_post_create_with_list_valid():
    user_data = [
        generate_user_data()
    ]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithList", json=user_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200

def test_get_user_login_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}", timeout=TIMEOUT)
    assert response.status_code == 200

def test_get_user_login_invalid_credentials():
    response = requests.get(f"{BASE_URL}/user/login?username=invalid&password=invalid", timeout=TIMEOUT)
    assert response.status_code == 400

def test_get_user_logout_valid():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}", timeout=TIMEOUT)
    response = requests.get(f"{BASE_URL}/user/logout", timeout=TIMEOUT)
    assert response.status_code == 200

# --- Integration Tests ---

def test_crud_pet_flow():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    # Create
    post_response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    pet_id = post_response.json()["id"]
    # Read
    get_response = requests.get(f"{BASE_URL}/pet/{pet_id}", timeout=TIMEOUT)
    assert get_response.status_code == 200
    # Update
    updated_data = pet_data.copy()
    updated_data["name"] = "updated_" + pet_data["name"]
    put_response = requests.put(f"{BASE_URL}/pet", json=updated_data, headers=headers, timeout=TIMEOUT)
    assert put_response.status_code == 200
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers=headers, timeout=TIMEOUT)
    assert delete_response.status_code == 200

def test_crud_store_order_flow():
    order_data = {
        "id": random.randint(1000, 9999),
        "petId": random.randint(1000, 9999),
        "quantity": 1,
        "shipDate": "2025-05-24T15:00:00.000Z",
        "status": "placed",
        "complete": False
    }
    headers = {"Content-Type": "application/json"}
    # Create
    post_response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    order_id = post_response.json()["id"]
    # Read
    get_response = requests.get(f"{BASE_URL}/store/order/{order_id}", timeout=TIMEOUT)
    assert get_response.status_code == 200
    # Update (not supported, so skip)
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/store/order/{order_id}", timeout=TIMEOUT)
    assert delete_response.status_code == 200

def test_crud_user_flow():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    # Create
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    # Read
    get_response = requests.get(f"{BASE_URL}/user/{user_data['username']}", timeout=TIMEOUT)
    assert get_response.status_code == 200
    # Update
    updated_data = user_data.copy()
    updated_data["firstName"] = "Updated"
    put_response = requests.put(f"{BASE_URL}/user/{user_data['username']}", json=updated_data, headers=headers, timeout=TIMEOUT)
    assert put_response.status_code == 200
    # Delete
    delete_response = requests.delete(f"{BASE_URL}/user/{user_data['username']}", timeout=TIMEOUT)
    assert delete_response.status_code == 200

def test_auth_and_access_flow():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    # Create user
    post_response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers, timeout=TIMEOUT)
    assert post_response.status_code == 200
    # Login
    login_response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}", timeout=TIMEOUT)
    assert login_response.status_code == 200
    # Access protected endpoint with valid api_key
    pet_data = generate_pet_data()
    headers["api_key"] = API_KEY
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    # Access with invalid api_key
    headers["api_key"] = "invalid"
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 401

# --- Resilience Tests ---

def test_rate_limit_pet_post():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    pet_data = generate_pet_data()
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers, timeout=TIMEOUT)
        assert response.status_code in [200, 429]  # Allow for rate-limiting

def test_large_payload_pet_post():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    large_data = {"name": "a" * 10000, "id": random.randint(1000, 9999), "category": {"id": 1, "name": "test"}, "photoUrls": ["http://test.com"], "tags": [{"id": 1, "name": "test"}], "status": "available"}
    response = requests.post(f"{BASE_URL}/pet", json=large_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code in [200, 400, 413]  # Allow for payload size rejection

def test_timeout_pet_get():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/pet/1000", timeout=0.001)

def test_rate_limit_user_login():
    for _ in range(10):
        response = requests.get(f"{BASE_URL}/user/login?username=test&password=test", timeout=TIMEOUT)
        assert response.status_code in [200, 400, 429]  # Allow for rate-limiting

def test_large_payload_user_post():
    headers = {"Content-Type": "application/json"}
    large_data = generate_user_data()
    large_data["username"] = "a" * 10000
    response = requests.post(f"{BASE_URL}/user", json=large_data, headers=headers, timeout=TIMEOUT)
    assert response.status_code in [200, 400, 413]  # Allow for payload size rejection

def test_timeout_user_get():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/user/testuser", timeout=0.001)