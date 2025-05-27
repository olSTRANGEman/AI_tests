import pytest
import requests
import random
import string
import time
from requests.exceptions import Timeout

BASE_URL = "https://petstore.swagger.io/v2"

# Helper functions
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_pet_data():
    return {
        "id": random.randint(1000000, 9999999),
        "name": random_string(),
        "category": {"id": random.randint(1, 100), "name": random_string()},
        "photoUrls": [f"http://{random_string()}.com"],
        "tags": [{"id": random.randint(1, 100), "name": random_string()}],
        "status": random.choice(["available", "pending", "sold"])
    }

def create_user_data():
    return {
        "id": random.randint(1000000, 9999999),
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
        "id": random.randint(1000000, 9999999),
        "petId": pet_id,
        "quantity": random.randint(1, 10),
        "shipDate": "2023-01-01T00:00:00.000Z",
        "status": "placed",
        "complete": False
    }

# Utility functions
def create_test_pet():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    return response.json()

def create_test_user():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    return response.json()

def create_test_order(pet_id):
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    return response.json()

# Common function to handle responses
def handle_response(response):
    content_type = response.headers.get('Content-Type', '')
    try:
        if 'application/json' in content_type:
            return response.json()
        else:
            return {"text": response.text}
    except ValueError:
        return {"text": response.text}

# Unit tests for /pet endpoint
def test_post_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    assert pet["name"] == pet_data["name"]
    assert pet["status"] == pet_data["status"]

def test_post_pet_missing_name():
    pet_data = create_pet_data()
    del pet_data["name"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_post_pet_invalid_status():
    pet_data = create_pet_data()
    pet_data["status"] = "invalid_status"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_put_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    
    pet = handle_response(response)
    pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", json=pet, headers=headers)
    assert response.status_code == 200
    assert handle_response(response)["name"] == pet["name"]

def test_put_pet_invalid_id():
    pet_data = create_pet_data()
    pet_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_get_pet_by_id_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert handle_response(response)["id"] == pet_id

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
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
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

# Unit tests for /pet/findByTags
def test_get_pets_by_tags_valid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "cat,dog"})
    assert response.status_code == 200

def test_get_pets_by_missing_tags():
    response = requests.get(f"{BASE_URL}/pet/findByTags")
    assert response.status_code == 400

# Unit tests for /pet/{petId} endpoint
def test_upload_pet_photo_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    pet_id = pet["id"]
    
    files = {'file': ('test.jpg', b'fake-image-data', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", files=files)
    assert response.status_code == 200

def test_upload_pet_missing_file():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    pet_id = pet["id"]
    
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", data={"additionalMetadata": "test"})
    assert response.status_code == 400

# Unit tests for /user endpoint
def test_post_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    user = handle_response(response)
    assert "username" in user

def test_post_user_duplicate_username():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_get_user_by_username_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    user = handle_response(response)
    username = user["username"]
    
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    assert handle_response(response)["username"] == username

def test_get_user_by_username_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_delete_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    user = handle_response(response)
    username = user["username"]
    
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 204

# Unit tests for /user/login
def test_login_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    
    params = {
        "login": user_data["username"],
        "password": "password123"
    }
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200

def test_login_invalid_credentials():
    params = {
        "login": "invalid_user",
        "password": "wrong_password"
    }
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 400

# Unit tests for /store/order endpoint
def test_post_order_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    pet_id = pet["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 200
    order = handle_response(response)
    assert order["petId"] == pet_id

def test_post_order_invalid_pet_id():
    order_data = create_order_data(9999999)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_get_order_by_id_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    pet_id = pet["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 200
    order = handle_response(response)
    order_id = order["id"]
    
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    assert handle_response(response)["id"] == order_id

def test_delete_order_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet = handle_response(response)
    pet_id = pet["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 200
    order = handle_response(response)
    order_id = order["id"]
    
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

# Unit tests for /store/inventory
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

# Integration tests
def test_crud_pet_flow():
    # Create
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    # Read
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert handle_response(response)["id"] == pet_id
    
    # Update
    updated_pet = pet_data.copy()
    updated_pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", json=updated_pet, headers=headers)
    assert response.status_code == 200
    assert handle_response(response)["name"] == updated_pet["name"]
    
    # Delete
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 204

def test_crud_user_flow():
    # Create
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    username = handle_response(response)["username"]
    
    # Read
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    assert handle_response(response)["username"] == username
    
    # Delete
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 204

def test_auth_and_access_flow():
    # Create user
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    
    # Login
    params = {
        "login": user_data["username"],
        "password": "password123"
    }
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200
    
    # Get user info with auth
    token = response.cookies.get("token") if response.cookies else None
    headers = {"api_key": token} if token else {}
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}", headers=headers)
    assert response.status_code == 200
    
    # Try with invalid token
    invalid_headers = {"api_key": "invalid_token"}
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}", headers=invalid_headers)
    assert response.status_code in [401, 403]

# Fuzz tests
def test_large_payload():
    large_data = create_pet_data()
    large_data["name"] = "A" * 100000
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=large_data, headers=headers)
    assert response.status_code in [413, 414, 411]

def test_rate_limiting():
    for _ in range(50):
        response = requests.get(f"{BASE_URL}/pet/1")
        if response.status_code == 429:
            break
    else:
        pytest.skip("Rate limiting not detected")

def test_timeout_handling():
    try:
        requests.get(f"{BASE_URL}/pet/1", timeout=0.0001)
    except Timeout:
        pass
    else:
        assert False, "Timeout not raised"

# Additional tests (continuation to reach 50)
def test_put_pet_missing_id():
    pet_data = create_pet_data()
    del pet_data["id"]
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_put_pet_missing_name():
    pet_data = create_pet_data()
    del pet_data["name"]
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_get_pet_invalid_path():
    response = requests.get(f"{BASE_URL}/pet/invalid/path")
    assert response.status_code == 404

def test_delete_pet_missing_id():
    response = requests.delete(f"{BASE_URL}/pet/")
    assert response.status_code == 404

def test_post_duplicate_pet_id():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_update_nonexistent_pet():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 404

def test_get_all_pets():
    response = requests.get(f"{BASE_URL}/pet")
    assert response.status_code == 405

def test_get_all_users():
    response = requests.get(f"{BASE_URL}/user")
    assert response.status_code == 405

def test_get_all_orders():
    response = requests.get(f"{BASE_URL}/store/order")
    assert response.status_code == 405

def test_create_order_missing_pet_id():
    order_data = create_order_data(None)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_quantity():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    order_data["quantity"] = -1
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_get_order_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.get(f"{BASE_URL}/store/order/{unique_id}")
    assert response.status_code == 404

def test_delete_order_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.delete(f"{BASE_URL}/store/order/{unique_id}")
    assert response.status_code == 404

def test_update_order_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 200
    order = handle_response(response)
    order_id = order["id"]
    
    updated_order = {
        "id": order_id,
        "petId": pet_id,
        "quantity": 2,
        "shipDate": "2023-01-02T00:00:00.000Z",
        "status": "approved",
        "complete": True
    }
    response = requests.put(f"{BASE_URL}/store/order", json=updated_order, headers=headers)
    assert response.status_code == 200
    assert handle_response(response)["status"] == "approved"

def test_update_order_invalid_status():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 200
    order = handle_response(response)
    order_id = order["id"]
    
    updated_order = {
        "id": order_id,
        "petId": pet_id,
        "quantity": 2,
        "shipDate": "2023-01-02T00:00:00.000Z",
        "status": "invalid_status",
        "complete": True
    }
    response = requests.put(f"{BASE_URL}/store/order", json=updated_order, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_username():
    user_data = create_user_data()
    del user_data["username"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_email():
    user_data = create_user_data()
    del user_data["email"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_update_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 200
    user = handle_response(response)
    username = user["username"]
    
    updated_user = {
        "username": username,
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code == 200

def test_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_invalid_username():
    response = requests.get(f"{BASE_URL}/user/invalid!@#username")
    assert response.status_code == 404

def test_create_pet_invalid_category():
    pet_data = create_pet_data()
    pet_data["category"] = {"id": "invalid", "name": random_string()}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_category():
    pet_data = create_pet_data()
    del pet_data["category"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_photo_url():
    pet_data = create_pet_data()
    pet_data["photoUrls"] = ["not_a_url"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_photo_url():
    pet_data = create_pet_data()
    del pet_data["photoUrls"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_tags():
    pet_data = create_pet_data()
    pet_data["tags"] = [{"id": "invalid", "name": random_string()}]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_tags():
    pet_data = create_pet_data()
    del pet_data["tags"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_ship_date():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    del order_data["shipDate"]
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_complete_flag():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    order_data["complete"] = "not_boolean"
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_status():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    del order_data["status"]
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_id():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    order_data = create_order_data(pet_id)
    order_data["id"] = "invalid_id"
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_password():
    user_data = create_user_data()
    user_data["password"] = "weak"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_phone():
    user_data = create_user_data()
    user_data["phone"] = "invalid_phone"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_first_name():
    user_data = create_user_data()
    del user_data["firstName"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_last_name():
    user_data = create_user_data()
    del user_data["lastName"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_status():
    user_data = create_user_data()
    user_data["userStatus"] = -1
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

# Additional tests for endpoints with low coverage
def test_upload_pet_image_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_id = handle_response(response)["id"]
    
    files = {'file': ('test.jpg', b'fake-image-data', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", data={"additionalMetadata": "test"}, files=files)
    assert response.status_code == 200

def test_get_store_order_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.get(f"{BASE_URL}/store/order/{unique_id}")
    assert response.status_code == 404

def test_create_user_with_array():
    users_data = []
    for _ in range(3):
        users_data.append(create_user_data())
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=users_data, headers=headers)
    assert response.status_code == 200

def test_create_user_with_list():
    users_data = []
    for _ in range(3):
        users_data.append(create_user_data())
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user/createWithList", json=users_data, headers=headers)
    assert response.status_code == 200

def test_user_login_logout_flow():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    
    # Login
    params = {
        "login": user_data["username"],
        "password": "password123"
    }
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200
    
    # Logout
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200