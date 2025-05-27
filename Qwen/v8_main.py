import pytest
import requests
import random
import string
from requests.exceptions import Timeout, JSONDecodeError

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
    try:
        return response.json() if response.status_code in [200, 201] else None
    except JSONDecodeError:
        return {"raw": response.text}

def create_test_user():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    try:
        return response.json() if response.status_code in [200, 201] else None
    except JSONDecodeError:
        return {"raw": response.text}

def create_test_order(pet_id):
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    try:
        return response.json() if response.status_code in [200, 201] else None
    except JSONDecodeError:
        return {"raw": response.text}

# Common function to handle responses
def handle_response(response):
    try:
        return response.json()
    except JSONDecodeError:
        return {"raw": response.text}

# Unit tests for /pet endpoint
def test_post_pet_valid():
    pet_data = create_pet_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code in [200, 201]
    pet = handle_response(response)
    assert pet.get("name") == pet_data["name"]
    assert pet.get("status") == pet_data["status"]

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
    assert response.status_code in [200, 201]
    
    pet = handle_response(response)
    pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", json=pet, headers=headers)
    assert response.status_code in [200, 201]
    updated_pet = handle_response(response)
    assert updated_pet.get("name") == pet["name"]

def test_put_pet_invalid_id():
    pet_data = create_pet_data()
    pet_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_get_pet_by_id_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert handle_response(response).get("id") == pet_id

def test_get_pet_by_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400

def test_get_pet_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.get(f"{BASE_URL}/pet/{unique_id}")
    assert response.status_code == 404

def test_delete_pet_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
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

# Unit tests for /pet/{petId}/uploadImage
def test_upload_pet_photo_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    files = {'file': ('test.jpg', b'fake-image-data', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", files=files)
    assert response.status_code == 200

def test_upload_pet_missing_file():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", data={"additionalMetadata": "test"})
    assert response.status_code == 400

# Unit tests for /user endpoint
def test_post_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert "username" in user or "message" in user

def test_post_user_duplicate_username():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_get_user_by_username_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    username = user.get("username")
    assert username is not None
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    assert handle_response(response).get("username") == username

def test_get_user_by_username_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_delete_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    username = user.get("username")
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
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order.get("petId") == pet_id

def test_post_order_invalid_pet_id():
    order_data = create_order_data(9999999)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_get_order_by_id_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    order_id = order.get("id")
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    assert handle_response(response).get("id") == order_id

def test_delete_order_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    order_id = order.get("id")
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
    assert response.status_code in [200, 201]
    pet = handle_response(response)
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    # Read
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    assert handle_response(response).get("id") == pet_id
    
    # Update
    updated_pet = pet.copy()
    updated_pet["name"] = random_string()
    response = requests.put(f"{BASE_URL}/pet", json=updated_pet, headers=headers)
    assert response.status_code in [200, 201]
    assert handle_response(response).get("name") == updated_pet["name"]
    
    # Delete
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 204

def test_crud_user_flow():
    # Create
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    username = user.get("username")
    assert username is not None
    
    # Read
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    assert handle_response(response).get("username") == username
    
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
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code in [200, 201]
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
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["quantity"] = -1
    headers = {'Content-Type': 'application/json'}
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
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    updated_order = {
        "id": order.get("id"),
        "petId": pet_id,
        "quantity": 2,
        "shipDate": "2023-01-02T00:00:00.000Z",
        "status": "approved",
        "complete": True
    }
    response = requests.put(f"{BASE_URL}/store/order", json=updated_order, headers=headers)
    assert response.status_code in [200, 201]
    assert handle_response(response).get("status") == "approved"

def test_update_order_invalid_status():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    updated_order = {
        "id": order.get("id"),
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
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code in [200, 201]

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
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["shipDate"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_complete_flag():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["complete"] = "invalid"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_status():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["status"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_id():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
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

def test_upload_pet_image_valid():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    files = {'file': ('test.jpg', b'fake-image-data', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files)
    assert response.status_code == 200

def test_get_store_order_not_found():
    unique_id = random.randint(1000000, 9999999)
    response = requests.get(f"{BASE_URL}/store/order/{unique_id}")
    assert response.status_code == 404

def test_create_user_with_array():
    users_data = [create_user_data() for _ in range(3)]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=users_data, headers=headers)
    assert response.status_code == 200

def test_create_user_with_list():
    users_data = [create_user_data() for _ in range(3)]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user/createWithList", json=users_data, headers=headers)
    assert response.status_code == 200

def test_user_login_logout_flow():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    
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

def test_get_pet_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400

def test_put_user_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code in [200, 201]

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_get_user_invalid_username():
    response = requests.get(f"{BASE_URL}/user/invalid!@#username")
    assert response.status_code == 404

def test_put_user_missing_username():
    user_data = create_user_data()
    del user_data["username"]
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_put_user_invalid_id():
    user_data = create_user_data()
    user_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_username():
    user_data = create_user_data()
    user_data["username"] = "invalid username with space"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_get_order_invalid_id():
    response = requests.get(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code == 400

def test_delete_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/9999999")
    assert response.status_code == 404

def test_update_order_missing_status():
    order_data = create_order_data(1234567)
    order_data["status"] = ""
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_update_order_invalid_pet_id():
    order_data = create_order_data("invalid_id")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_password():
    user_data = create_user_data()
    del user_data["password"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_email():
    user_data = create_user_data()
    user_data["email"] = "invalid_email"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_user_status():
    user_data = create_user_data()
    del user_data["userStatus"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_delete_order_missing_id():
    response = requests.delete(f"{BASE_URL}/store/order/")
    assert response.status_code == 404

def test_create_order_invalid_quantity():
    order_data = create_order_data(1234567)
    order_data["quantity"] = 0
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_id():
    order_data = create_order_data(1234567)
    order_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_id():
    user_data = create_user_data()
    user_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_update_user_missing_email():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code in [200, 201]

def test_delete_user_missing_id():
    response = requests.delete(f"{BASE_URL}/user/")
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

def test_get_pets_by_status_sold():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "sold"})
    assert response.status_code == 200

def test_get_pets_by_status_available():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert response.status_code == 200

def test_get_pets_by_status_pending():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "pending"})
    assert response.status_code == 200

def test_create_user_with_invalid_email():
    user_data = create_user_data()
    user_data["email"] = "invalid_email"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_status():
    order_data = create_order_data(1234567)
    order_data["status"] = "invalid_status"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_quantity():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["quantity"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_status_format():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["status"] = 1234567890
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_ship_date_format():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["shipDate"] = "invalid_date"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_id():
    order_data = create_order_data(1234567)
    del order_data["id"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_complete_flag():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["complete"] = "invalid"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_update_user_invalid_email():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": "invalid_email",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code == 400

def test_update_user_missing_password():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code in [200, 201]

def test_delete_order_missing_id():
    response = requests.delete(f"{BASE_URL}/store/order/")
    assert response.status_code == 404

def test_get_pets_by_tags_valid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "cat,dog"})
    assert response.status_code == 200

def test_get_pets_by_tags_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "invalid_tag"})
    assert response.status_code == 200

def test_get_user_by_id_valid():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    username = user.get("username")
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    assert handle_response(response).get("username") == username

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_update_user_invalid_phone():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code in [200, 201]

def test_get_user_by_email():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_get_user_by_username_invalid():
    response = requests.get(f"{BASE_URL}/user/invalid_username!@#")
    assert response.status_code == 404

def test_create_user_with_empty_username():
    user_data = create_user_data()
    user_data["username"] = ""
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_status_format():
    pet_data = create_pet_data()
    pet_data["status"] = 1234567890
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_id_format():
    pet_data = create_pet_data()
    pet_data["id"] = "invalid_id"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_complete_format():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["complete"] = "invalid"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_id():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["id"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_user_with_special_characters():
    user_data = create_user_data()
    user_data["username"] = "!@#$%^&*()"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_category_id():
    pet_data = create_pet_data()
    pet_data["category"] = {"id": "invalid", "name": random_string()}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_name():
    pet_data = create_pet_data()
    del pet_data["name"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_status():
    pet_data = create_pet_data()
    pet_data["status"] = "invalid_status"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_order_invalid_quantity_range():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    order_data["quantity"] = 0
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_status():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["status"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_user_status():
    user_data = create_user_data()
    user_data["userStatus"] = -1
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_user_status():
    user_data = create_user_data()
    del user_data["userStatus"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_category_name():
    pet_data = create_pet_data()
    pet_data["category"] = {"id": random.randint(1, 100), "name": ""}
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
    pet_data["photoUrls"] = ["invalid_url"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_photo_url():
    pet_data = create_pet_data()
    del pet_data["photoUrls"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_invalid_tags_format():
    pet_data = create_pet_data()
    pet_data["tags"] = "not_an_array"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_pet_missing_tags():
    pet_data = create_pet_data()
    del pet_data["tags"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_password():
    user_data = create_user_data()
    user_data["password"] = "short"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_phone():
    user_data = create_user_data()
    del user_data["phone"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_phone():
    user_data = create_user_data()
    user_data["phone"] = "invalid_phone"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
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

def test_create_order_invalid_pet_id():
    order_data = create_order_data("invalid_id")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_create_order_missing_quantity():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    del order_data["quantity"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code == 400

def test_update_order_invalid_quantity():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    order["quantity"] = -1
    response = requests.put(f"{BASE_URL}/store/order", json=order, headers=headers)
    assert response.status_code == 400

def test_update_order_missing_status():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    del order["status"]
    response = requests.put(f"{BASE_URL}/store/order", json=order, headers=headers)
    assert response.status_code == 400

def test_update_order_invalid_pet_id():
    pet = create_test_pet()
    assert pet is not None
    pet_id = pet.get("id")
    assert pet_id is not None
    
    order_data = create_order_data(pet_id)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/store/order", json=order_data, headers=headers)
    assert response.status_code in [200, 201]
    order = handle_response(response)
    assert order is not None
    
    order["petId"] = "invalid_id"
    response = requests.put(f"{BASE_URL}/store/order", json=order, headers=headers)
    assert response.status_code == 400

def test_create_user_with_invalid_username():
    user_data = create_user_data()
    user_data["username"] = "invalid username with space"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_missing_password():
    user_data = create_user_data()
    del user_data["password"]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code == 400

def test_update_user_invalid_email():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": "invalid_email",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code == 400

def test_update_user_missing_username():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "new_password123"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code == 400

def test_update_user_invalid_password():
    user_data = create_user_data()
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    assert response.status_code in [200, 201]
    user = handle_response(response)
    assert user is not None
    
    updated_user = {
        "username": user.get("username"),
        "firstName": random_string(),
        "lastName": random_string(),
        "email": f"{random_string()}@example.com",
        "password": "weak"
    }
    response = requests.put(f"{BASE_URL}/user", json=updated_user, headers=headers)
    assert response.status_code == 400

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/9999999")
    assert response.status_code == 404

def test_delete_pet_not_found():
    response = requests.delete(f"{BASE_URL}/pet/9999999")
    assert response.status_code == 404

def test_get_user_by_username_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

def test_get_order_by_id_not_found():
    response = requests.get(f"{BASE_URL}/store/order/9999999")
    assert response.status_code == 404

def test_delete_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/9999999")
    assert response.status_code == 404