import pytest
import requests
import time
import random
import string
from datetime import datetime

BASE_URL = "https://petstore.swagger.io/v2"
API_KEY = "special-key"  # As per Swagger spec for protected endpoints

# Helper to generate unique IDs/names
def generate_unique_id():
    return int(datetime.now().timestamp() * 1000)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Helper to validate response schema
def validate_pet_schema(response_json):
    assert isinstance(response_json, dict), "Response is not a dictionary"
    assert "id" in response_json, "Missing 'id' in response"
    assert isinstance(response_json["id"], int), "'id' is not an integer"
    assert "name" in response_json, "Missing 'name' in response"
    assert isinstance(response_json["name"], str), "'name' is not a string"

def validate_user_schema(response_json):
    assert isinstance(response_json, dict), "Response is not a dictionary"
    assert "id" in response_json, "Missing 'id' in response"
    assert isinstance(response_json["id"], int), "'id' is not an integer"
    assert "username" in response_json, "Missing 'username' in response"
    assert isinstance(response_json["username"], str), "'username' is not a string"

def validate_order_schema(response_json):
    assert isinstance(response_json, dict), "Response is not a dictionary"
    assert "id" in response_json, "Missing 'id' in response"
    assert isinstance(response_json["id"], int), "'id' is not an integer"
    assert "status" in response_json, "Missing 'status' in response"
    assert isinstance(response_json["status"], str), "'status' is not a string"

# --- /pet Endpoint Tests ---

def test_post_pet_valid():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_pet_schema(response.json())

def test_post_pet_invalid_id():
    data = {
        "id": "invalid",
        "name": "dog_invalid",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid ID

def test_post_pet_missing_name():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

def test_post_pet_form_data():
    pet_id = generate_unique_id()
    data = {
        "id": str(pet_id),
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_get_pet_by_id_valid():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_pet_schema(response.json())

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_get_pet_by_id_invalid():
    response = requests.get(f"{BASE_URL}/pet/invalid")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"  # API returns 404 for invalid ID

def test_put_pet_valid():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    update_data = {
        "id": pet_id,
        "name": f"dog_updated_{pet_id}",
        "status": "sold"
    }
    response = requests.put(f"{BASE_URL}/pet", json=update_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_pet_schema(response.json())

def test_put_pet_invalid_id():
    data = {
        "id": "invalid",
        "name": "dog_invalid",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.put(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid ID

def test_put_pet_not_found():
    data = {
        "id": 999999999,
        "name": "dog_not_found",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.put(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_put_pet_form_data():
    pet_id = generate_unique_id()
    data = {
        "id": str(pet_id),
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.put(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_delete_pet_valid():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_delete_pet_not_found():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/pet/999999999", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_delete_pet_invalid_id():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/pet/invalid", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"  # API returns 404 for invalid ID

def test_post_pet_form_valid():
    pet_id = generate_unique_id()
    data = {
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files={"file": ("test.txt", b"test content")}, data=data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_post_pet_form_invalid_id():
    data = {
        "name": "dog_invalid",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet/invalid/uploadImage", files={"file": ("test.txt", b"test content")}, data=data, headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"  # API returns 404 for invalid ID

def test_get_pet_find_by_status_valid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert isinstance(response.json(), list), "Response is not a list"

def test_get_pet_find_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid_status"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == [], "Expected empty list for invalid status"

# --- /store Endpoint Tests ---

def test_post_store_order_valid():
    order_id = generate_unique_id()
    data = {
        "id": order_id,
        "petId": generate_unique_id(),
        "quantity": 1,
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_order_schema(response.json())

def test_post_store_order_invalid_quantity():
    data = {
        "id": generate_unique_id(),
        "petId": generate_unique_id(),
        "quantity": "invalid",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid quantity

def test_post_store_order_form_data():
    order_id = generate_unique_id()
    data = {
        "id": str(order_id),
        "petId": str(generate_unique_id()),
        "quantity": "1",
        "status": "placed",
        "complete": "true"
    }
    response = requests.post(f"{BASE_URL}/store/order", data=data)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_get_store_order_by_id_valid():
    order_id = generate_unique_id()
    data = {
        "id": order_id,
        "petId": generate_unique_id(),
        "quantity": 1,
        "status": "placed",
        "complete": True
    }
    requests.post(f"{BASE_URL}/store/order", json=data)
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_order_schema(response.json())

def test_get_store_order_by_id_not_found():
    response = requests.get(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_get_store_order_by_id_invalid():
    response = requests.get(f"{BASE_URL}/store/order/invalid")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"  # API returns 404 for invalid ID

def test_delete_store_order_valid():
    order_id = generate_unique_id()
    data = {
        "id": order_id,
        "petId": generate_unique_id(),
        "quantity": 1,
        "status": "placed",
        "complete": True
    }
    requests.post(f"{BASE_URL}/store/order", json=data)
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_delete_store_order_not_found():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/store/order/999999999", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_delete_store_order_invalid_id():
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/store/order/invalid", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"  # API returns 404 for invalid ID

def test_get_store_inventory():
    headers = {"api_key": API_KEY}
    response = requests.get(f"{BASE_URL}/store/inventory", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert isinstance(response.json(), dict), "Response is not a dictionary"

# --- /user Endpoint Tests ---

def test_post_user_valid():
    username = f"user_{generate_random_string()}"
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_post_user_invalid_email():
    data = {
        "id": generate_unique_id(),
        "username": f"user_{generate_random_string()}",
        "firstName": "John",
        "lastName": "Doe",
        "email": "invalid_email",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid email

def test_post_user_form_data():
    username = f"user_{generate_random_string()}"
    data = {
        "id": str(generate_unique_id()),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    response = requests.post(f"{BASE_URL}/user", data=data)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_get_user_by_name_valid():
    username = f"user_{generate_random_string()}"
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    requests.post(f"{BASE_URL}/user", json=data)
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    validate_user_schema(response.json())

def test_get_user_by_name_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_put_user_valid():
    username = f"user_{generate_random_string()}"
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    requests.post(f"{BASE_URL}/user", json=data)
    update_data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "Jane",
        "lastName": "Doe",
        "email": f"updated_{username}@example.com",
        "password": "newpass123",
        "phone": "0987654321",
        "userStatus": 2
    }
    response = requests.put(f"{BASE_URL}/user/{username}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_put_user_not_found():
    data = {
        "id": generate_unique_id(),
        "username": "nonexistent_user",
        "firstName": "John",
        "lastName": "Doe",
        "email": "nonexistent@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.put(f"{BASE_URL}/user/nonexistent_user", json=data)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_put_user_form_data():
    username = f"user_{generate_random_string()}"
    data = {
        "id": str(generate_unique_id()),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    response = requests.put(f"{BASE_URL}/user/{username}", data=data)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_delete_user_valid():
    username = f"user_{generate_random_string()}"
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    requests.post(f"{BASE_URL}/user", json=data)
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_post_user_create_with_array_valid():
    data = [
        {
            "id": generate_unique_id(),
            "username": f"user1_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": f"user1_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        },
        {
            "id": generate_unique_id(),
            "username": f"user2_{generate_random_string()}",
            "firstName": "Jane",
            "lastName": "Doe",
            "email": f"user2_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        }
    ]
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_post_user_create_with_array_invalid():
    data = [
        {
            "id": "invalid",
            "username": f"user_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid_email",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        }
    ]
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=data)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid data

def test_post_user_create_with_array_form_data():
    data = [
        {
            "id": str(generate_unique_id()),
            "username": f"user1_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": f"user1_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": "1"
        }
    ]
    form_data = {}
    for i, user in enumerate(data):
        for key, value in user.items():
            form_data[f"user[{i}][{key}]"] = value
    response = requests.post(f"{BASE_URL}/user/createWithArray", data=form_data)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_post_user_create_with_list_valid():
    data = [
        {
            "id": generate_unique_id(),
            "username": f"user1_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": f"user1_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        },
        {
            "id": generate_unique_id(),
            "username": f"user2_{generate_random_string()}",
            "firstName": "Jane",
            "lastName": "Doe",
            "email": f"user2_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        }
    ]
    response = requests.post(f"{BASE_URL}/user/createWithList", json=data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_post_user_create_with_list_invalid():
    data = [
        {
            "id": "invalid",
            "username": f"user_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid_email",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": 1
        }
    ]
    response = requests.post(f"{BASE_URL}/user/createWithList", json=data)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for invalid data

def test_post_user_create_with_list_form_data():
    data = [
        {
            "id": str(generate_unique_id()),
            "username": f"user1_{generate_random_string()}",
            "firstName": "John",
            "lastName": "Doe",
            "email": f"user1_{generate_random_string()}@example.com",
            "password": "pass123",
            "phone": "1234567890",
            "userStatus": "1"
        }
    ]
    form_data = {}
    for i, user in enumerate(data):
        for key, value in user.items():
            form_data[f"user[{i}][{key}]"] = value
    response = requests.post(f"{BASE_URL}/user/createWithList", data=form_data)
    assert response.status_code == 415, f"Expected 415, got {response.status_code}"

def test_get_user_login_valid():
    username = f"user_{generate_random_string()}"
    password = "pass123"
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": password,
        "phone": "1234567890",
        "userStatus": 1
    }
    requests.post(f"{BASE_URL}/user", json=data)
    response = requests.get(f"{BASE_URL}/user/login", params={"username": username, "password": password})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_get_user_login_invalid():
    response = requests.get(f"{BASE_URL}/user/login", params={"username": "nonexistent", "password": "wrong"})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

def test_get_user_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# --- Integration Tests ---

def test_crud_pet_flow():
    pet_id = generate_unique_id()
    # Create
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code == 200, f"Create: Expected 200, got {response.status_code}"
    # Read
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200, f"Read: Expected 200, got {response.status_code}"
    validate_pet_schema(response.json())
    # Update
    update_data = {
        "id": pet_id,
        "name": f"dog_updated_{pet_id}",
        "status": "sold"
    }
    response = requests.put(f"{BASE_URL}/pet", json=update_data, headers=headers)
    assert response.status_code == 200, f"Update: Expected 200, got {response.status_code}"
    # Delete
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers=headers)
    assert response.status_code == 200, f"Delete: Expected 200, got {response.status_code}"

def test_crud_store_flow():
    order_id = generate_unique_id()
    # Create
    data = {
        "id": order_id,
        "petId": generate_unique_id(),
        "quantity": 1,
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 200, f"Create: Expected 200, got {response.status_code}"
    # Read
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200, f"Read: Expected 200, got {response.status_code}"
    validate_order_schema(response.json())
    # Delete
    headers = {"api_key": API_KEY}
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}", headers=headers)
    assert response.status_code == 200, f"Delete: Expected 200, got {response.status_code}"

def test_crud_user_flow():
    username = f"user_{generate_random_string()}"
    # Create
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == 200, f"Create: Expected 200, got {response.status_code}"
    # Read
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200, f"Read: Expected 200, got {response.status_code}"
    validate_user_schema(response.json())
    # Update
    update_data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "Jane",
        "lastName": "Doe",
        "email": f"updated_{username}@example.com",
        "password": "newpass123",
        "phone": "0987654321",
        "userStatus": 2
    }
    response = requests.put(f"{BASE_URL}/user/{username}", json=update_data)
    assert response.status_code == 200, f"Update: Expected 200, got {response.status_code}"
    # Delete
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200, f"Delete: Expected 200, got {response.status_code}"

def test_auth_and_access_flow():
    username = f"user_{generate_random_string()}"
    password = "pass123"
    # Create user
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": password,
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == 200, f"Create user: Expected 200, got {response.status_code}"
    # Login
    response = requests.get(f"{BASE_URL}/user/login", params={"username": username, "password": password})
    assert response.status_code == 200, f"Login: Expected 200, got {response.status_code}"
    # Protected endpoint with valid api_key
    pet_id = generate_unique_id()
    pet_data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200, f"Protected request: Expected 200, got {response.status_code}"
    # Protected endpoint with invalid api_key
    headers = {"api_key": "invalid_key"}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 401, f"Invalid auth: Expected 401, got {response.status_code}"

# --- Resilience Tests ---

def test_post_pet_rate_limit():
    headers = {"api_key": API_KEY}
    for _ in range(10):
        pet_id = generate_unique_id()
        data = {
            "id": pet_id,
            "name": f"dog_{pet_id}",
            "status": "available"
        }
        response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}"

def test_post_pet_large_payload():
    pet_id = generate_unique_id()
    large_string = "a" * 10**6  # 1MB string
    data = {
        "id": pet_id,
        "name": large_string,
        "status": "available"
    }
    headers = {"api_key": API_KEY}
    response = requests.post(f"{BASE_URL}/pet", json=data, headers=headers)
    assert response.status_code in [200, 400, 413], f"Expected 200, 400, or 413, got {response.status_code}"

def test_get_pet_timeout():
    pet_id = generate_unique_id()
    try:
        response = requests.get(f"{BASE_URL}/pet/{pet_id}", timeout=0.001)
    except requests.exceptions.Timeout:
        assert True, "Expected Timeout exception"
    else:
        assert False, f"Expected Timeout, but got response with status {response.status_code}"

def test_get_store_inventory_rate_limit():
    headers = {"api_key": API_KEY}
    for _ in range(10):
        response = requests.get(f"{BASE_URL}/store/inventory", headers=headers)
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}"

def test_post_user_large_payload():
    username = f"user_{generate_random_string()}"
    large_string = "a" * 10**6  # 1MB string
    data = {
        "id": generate_unique_id(),
        "username": username,
        "firstName": large_string,
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "pass123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code in [200, 400, 413], f"Expected 200, 400, or 413, got {response.status_code}"

def test_get_user_timeout():
    try:
        response = requests.get(f"{BASE_URL}/user/nonexistent_user", timeout=0.001)
    except requests.exceptions.Timeout:
        assert True, "Expected Timeout exception"
    else:
        assert False, f"Expected Timeout, but got response with status {response.status_code}"

# Additional tests to ensure coverage of status codes and edge cases

def test_post_pet_unauthorized():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": f"dog_{pet_id}",
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", json=data)  # No api_key
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

def test_delete_pet_unauthorized():
    pet_id = generate_unique_id()
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")  # No api_key
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

def test_get_pet_find_by_status_empty():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": ""})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

def test_post_user_missing_required():
    data = {
        "id": generate_unique_id(),
        "firstName": "John",
        "lastName": "Doe"
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"  # API returns 500 for missing required fields

def test_put_user_invalid_method():
    response = requests.post(f"{BASE_URL}/user/nonexistent_user", json={})
    assert response.status_code == 405, f"Expected 405, got {response.status_code}"

def test_delete_store_order_unauthorized():
    order_id = generate_unique_id()
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")  # No api_key
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"