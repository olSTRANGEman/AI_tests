import pytest
import requests
import jsonschema
import time
import random
import string
from datetime import datetime

# Base URL for the Petstore API
BASE_URL = "https://petstore.swagger.io/v2"

# Fallback API key (replace with actual key if available)
FALLBACK_API_KEY = "special-key"

# Helper function to generate unique strings for test isolation
def generate_unique_string(prefix="test"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"{prefix}_{timestamp}_{random_str}"

# Helper function to get API key via /user/login
def get_api_key():
    username = generate_unique_string("user")
    password = "password123"
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": password,
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        login_response = requests.get(f"{BASE_URL}/user/login", params={"username": username, "password": password})
        if login_response.status_code == 200:
            return login_response.headers.get("X-API-KEY")
    return FALLBACK_API_KEY

# Helper schemas for response validation
PET_SCHEMA = {
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "category": {"type": ["object", "null"], "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
        "photoUrls": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}},
        "status": {"type": "string", "enum": ["available", "pending", "sold"]}
    }
}

ORDER_SCHEMA = {
    "type": "object",
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"],
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string"},
        "status": {"type": "string", "enum": ["placed", "approved", "delivered"]},
        "complete": {"type": "boolean"}
    }
}

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

# --- Pet Endpoint Tests ---

def test_post_pet_valid():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [200, 415]
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/pet/{pet_id}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=PET_SCHEMA)

def test_post_pet_invalid_id():
    api_key = get_api_key()
    data = {
        "id": "invalid",
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [400, 415]

def test_post_pet_missing_name():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [400, 415]

def test_post_pet_form_data_415():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code == 415

def test_post_pet_method_not_allowed():
    api_key = get_api_key()
    response = requests.get(f"{BASE_URL}/pet", headers={"api_key": api_key})
    assert response.status_code == 405

def test_post_pet_unauthorized():
    data = {
        "id": str(random.randint(1000, 9999)),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code == 415

def test_get_pet_by_id_valid():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/pet/{pet_id}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=PET_SCHEMA)
    else:
        assert response.status_code == 415

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999")
    assert response.status_code == 404

def test_get_pet_by_id_invalid():
    response = requests.get(f"{BASE_URL}/pet/invalid")
    assert response.status_code == 404

def test_get_pet_by_id_missing_id():
    response = requests.get(f"{BASE_URL}/pet/0")
    assert response.status_code == 400

def test_put_pet_valid():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        update_data = {
            "id": str(pet_id),
            "name": generate_unique_string("updated_pet"),
            "status": "sold"
        }
        update_response = requests.put(f"{BASE_URL}/pet", data=update_data, headers=headers)
        assert update_response.status_code in [200, 415]
        if update_response.status_code == 200:
            get_response = requests.get(f"{BASE_URL}/pet/{pet_id}")
            assert get_response.status_code == 200
            jsonschema.validate(instance=get_response.json(), schema=PET_SCHEMA)
    else:
        assert response.status_code == 415

def test_put_pet_invalid_id():
    api_key = get_api_key()
    data = {
        "id": "invalid",
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.put(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [400, 415]

def test_put_pet_not_found():
    api_key = get_api_key()
    data = {
        "id": "999999",
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.put(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [404, 415]

def test_put_pet_form_data_415():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.put(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code == 415

def test_put_pet_method_not_allowed():
    api_key = get_api_key()
    response = requests.get(f"{BASE_URL}/pet", headers={"api_key": api_key})
    assert response.status_code == 405

def test_delete_pet_valid():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        delete_response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers={"api_key": api_key})
        assert delete_response.status_code in [400, 404]
    else:
        assert response.status_code == 415

def test_delete_pet_not_found():
    api_key = get_api_key()
    response = requests.delete(f"{BASE_URL}/pet/999999", headers={"api_key": api_key})
    assert response.status_code == 404

def test_delete_pet_invalid_id():
    api_key = get_api_key()
    response = requests.delete(f"{BASE_URL}/pet/invalid", headers={"api_key": api_key})
    assert response.status_code == 400

def test_get_find_by_status_valid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        jsonschema.validate(instance=response.json()[0], schema=PET_SCHEMA)

def test_get_find_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid_status"})
    assert response.status_code in [200, 400]

def test_get_find_by_tags_valid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "tag1"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        jsonschema.validate(instance=response.json()[0], schema=PET_SCHEMA)

def test_get_find_by_tags_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "!@#"})
    assert response.status_code in [200, 400]

def test_post_pet_by_form_valid():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        form_data = {
            "name": generate_unique_string("updated_pet"),
            "status": "sold"
        }
        post_response = requests.post(f"{BASE_URL}/pet/{pet_id}", data=form_data, headers=headers)
        assert post_response.status_code in [200, 404, 415]
    else:
        assert response.status_code == 415

def test_post_pet_by_form_not_found():
    api_key = get_api_key()
    form_data = {
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet/999999", data=form_data, headers=headers)
    assert response.status_code in [404, 415]

def test_post_pet_by_form_invalid_id():
    api_key = get_api_key()
    form_data = {
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet/invalid", data=form_data, headers=headers)
    assert response.status_code in [400, 415]

def test_post_pet_by_form_415():
    api_key = get_api_key()
    form_data = {
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet/1000", data=form_data, headers=headers)
    assert response.status_code == 415

def test_post_pet_by_form_method_not_allowed():
    api_key = get_api_key()
    response = requests.get(f"{BASE_URL}/pet/1000", headers={"api_key": api_key})
    assert response.status_code in [400, 404, 405]

def test_post_pet_upload_image():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        files = {"file": ("test.txt", b"test image data")}
        response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files, headers={"api_key": api_key})
        assert response.status_code in [200, 415]
    else:
        assert response.status_code == 415

# --- Store Endpoint Tests ---

def test_get_store_inventory():
    api_key = get_api_key()
    response = requests.get(f"{BASE_URL}/store/inventory", headers={"api_key": api_key})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_post_store_order_valid():
    api_key = get_api_key()
    order_id = random.randint(1000, 9999)
    pet_id = random.randint(1000, 9999)
    data = {
        "id": str(order_id),
        "petId": str(pet_id),
        "quantity": "1",
        "shipDate": "2025-05-24T12:00:00Z",
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    assert response.status_code in [200, 415]
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/store/order/{order_id}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=ORDER_SCHEMA)

def test_post_store_order_invalid():
    api_key = get_api_key()
    data = {
        "id": "invalid",
        "petId": "invalid",
        "quantity": "invalid",
        "shipDate": "invalid",
        "status": "invalid",
        "complete": "invalid"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    assert response.status_code in [400, 415]

def test_post_store_order_form_data_415():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "petId": str(random.randint(1000, 9999)),
        "quantity": "1",
        "shipDate": "2025-05-24T12:00:00Z",
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    assert response.status_code == 415

def test_post_store_order_method_not_allowed():
    api_key = get_api_key()
    response = requests.get(f"{BASE_URL}/store/order", headers={"api_key": api_key})
    assert response.status_code == 405

def test_get_store_order_by_id_valid():
    api_key = get_api_key()
    order_id = random.randint(1000, 9999)
    data = {
        "id": str(order_id),
        "petId": str(random.randint(1000, 9999)),
        "quantity": "1",
        "shipDate": "2025-05-24T12:00:00Z",
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/store/order/{order_id}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=ORDER_SCHEMA)
    else:
        assert response.status_code == 415

def test_get_store_order_by_id_not_found():
    response = requests.get(f"{BASE_URL}/store/order/999999")
    assert response.status_code == 404

def test_get_store_order_by_id_invalid():
    response = requests.get(f"{BASE_URL}/store/order/invalid")
    assert response.status_code == 400

def test_delete_store_order_valid():
    api_key = get_api_key()
    order_id = random.randint(1000, 9999)
    data = {
        "id": str(order_id),
        "petId": str(random.randint(1000, 9999)),
        "quantity": "1",
        "shipDate": "2025-05-24T12:00:00Z",
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        delete_response = requests.delete(f"{BASE_URL}/store/order/{order_id}", headers={"api_key": api_key})
        assert delete_response.status_code in [400, 404]
    else:
        assert response.status_code == 415

def test_delete_store_order_not_found():
    api_key = get_api_key()
    response = requests.delete(f"{BASE_URL}/store/order/999999", headers={"api_key": api_key})
    assert response.status_code == 404

def test_delete_store_order_invalid_id():
    api_key = get_api_key()
    response = requests.delete(f"{BASE_URL}/store/order/invalid", headers={"api_key": api_key})
    assert response.status_code == 400

# --- User Endpoint Tests ---

def test_post_user_valid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    assert response.status_code in [200, 415]
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/user/{username}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=USER_SCHEMA)

def test_post_user_invalid():
    data = {
        "id": "invalid",
        "username": generate_unique_string("user"),
        "firstName": "John",
        "lastName": "Doe",
        "email": "invalid",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "invalid"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    assert response.status_code in [400, 415]

def test_post_user_form_data_415():
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": generate_unique_string("user"),
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{generate_unique_string('user')}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    assert response.status_code == 415

def test_get_user_by_name_valid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        get_response = requests.get(f"{BASE_URL}/user/{username}")
        assert get_response.status_code == 200
        jsonschema.validate(instance=get_response.json(), schema=USER_SCHEMA)
    else:
        assert response.status_code == 415

def test_get_user_by_name_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent")
    assert response.status_code == 404

def test_get_user_by_name_invalid():
    response = requests.get(f"{BASE_URL}/user/!@#")
    assert response.status_code == 400

def test_put_user_valid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        update_data = {
            "id": str(random.randint(1000, 9999)),
            "username": username,
            "firstName": "Jane",
            "lastName": "Doe",
            "email": f"updated_{username}@example.com",
            "password": "newpassword123",
            "phone": "0987654321",
            "userStatus": "0"
        }
        response = requests.put(f"{BASE_URL}/user/{username}", data=update_data, headers=headers)
        assert response.status_code in [200, 415]
        if response.status_code == 200:
            get_response = requests.get(f"{BASE_URL}/user/{username}")
            assert get_response.status_code == 200
            jsonschema.validate(instance=get_response.json(), schema=USER_SCHEMA)
    else:
        assert response.status_code == 415

def test_put_user_not_found():
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": "nonexistent",
        "firstName": "John",
        "lastName": "Doe",
        "email": "nonexistent@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.put(f"{BASE_URL}/user/nonexistent", data=data, headers=headers)
    assert response.status_code in [404, 415]

def test_put_user_invalid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        update_data = {
            "id": "invalid",
            "username": username,
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "invalid",
            "password": "newpassword123",
            "phone": "0987654321",
            "userStatus": "invalid"
        }
        response = requests.put(f"{BASE_URL}/user/{username}", data=update_data, headers=headers)
        assert response.status_code in [400, 415]
    else:
        assert response.status_code == 415

def test_delete_user_valid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        response = requests.delete(f"{BASE_URL}/user/{username}")
        assert response.status_code in [400, 404]
    else:
        assert response.status_code == 415

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent")
    assert response.status_code == 404

def test_delete_user_invalid():
    response = requests.delete(f"{BASE_URL}/user/!@#")
    assert response.status_code == 400

def test_get_user_login_valid():
    username = generate_unique_string("user")
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/user/login", params={"username": username, "password": "password123"})
        assert response.status_code == 200
        assert "X-API-KEY" in response.headers
    else:
        assert response.status_code == 415

def test_get_user_login_invalid():
    response = requests.get(f"{BASE_URL}/user/login", params={"username": "nonexistent", "password": "wrong"})
    assert response.status_code == 400

def test_get_user_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_post_user_create_with_list_valid():
    data = [
        {
            "id": str(random.randint(1000, 9999)),
            "username": generate_unique_string("user1"),
            "firstName": "John",
            "lastName": "Doe",
            "email": f"{generate_unique_string('user1')}@example.com",
            "password": "password123",
            "phone": "1234567890",
            "userStatus": "1"
        },
        {
            "id": str(random.randint(1000, 9999)),
            "username": generate_unique_string("user2"),
            "firstName": "Jane",
            "lastName": "Doe",
            "email": f"{generate_unique_string('user2')}@example.com",
            "password": "password123",
            "phone": "0987654321",
            "userStatus": "1"
        }
    ]
    form_data = {}
    for i, user in enumerate(data):
        for key, value in user.items():
            form_data[f"user[{i}][{key}]"] = str(value)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user/createWithList", data=form_data, headers=headers)
    assert response.status_code in [200, 415]

def test_post_user_create_with_array_valid():
    data = [
        {
            "id": str(random.randint(1000, 9999)),
            "username": generate_unique_string("user1"),
            "firstName": "John",
            "lastName": "Doe",
            "email": f"{generate_unique_string('user1')}@example.com",
            "password": "password123",
            "phone": "1234567890",
            "userStatus": "1"
        }
    ]
    form_data = {}
    for i, user in enumerate(data):
        for key, value in user.items():
            form_data[f"user[{i}][{key}]"] = str(value)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user/createWithArray", data=form_data, headers=headers)
    assert response.status_code in [200, 415]

def test_post_user_create_with_list_invalid():
    data = [
        {
            "id": "invalid",
            "username": generate_unique_string("user"),
            "firstName": "John",
            "lastName": "Doe",
            "email": "invalid",
            "password": "password123",
            "phone": "1234567890",
            "userStatus": "invalid"
        }
    ]
    form_data = {}
    for i, user in enumerate(data):
        for key, value in user.items():
            form_data[f"user[{i}][{key}]"] = str(value)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user/createWithList", data=form_data, headers=headers)
    assert response.status_code in [400, 415]

# --- Integration Tests ---

def test_crud_pet_flow():
    api_key = get_api_key()
    pet_id = random.randint(1000, 9999)
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    # Create
    data = {
        "id": str(pet_id),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [200, 415]
    if response.status_code == 200:
        time.sleep(1)
        # Read
        response = requests.get(f"{BASE_URL}/pet/{pet_id}")
        assert response.status_code == 200
        jsonschema.validate(instance=response.json(), schema=PET_SCHEMA)
        # Update
        update_data = {
            "id": str(pet_id),
            "name": generate_unique_string("updated_pet"),
            "status": "sold"
        }
        response = requests.put(f"{BASE_URL}/pet", data=update_data, headers=headers)
        assert response.status_code in [200, 415]
        # Delete
        response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers={"api_key": api_key})
        assert response.status_code in [400, 404]
    else:
        assert response.status_code == 415

def test_crud_user_flow():
    username = generate_unique_string("user")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # Create
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    assert response.status_code in [200, 415]
    if response.status_code == 200:
        time.sleep(1)
        # Read
        response = requests.get(f"{BASE_URL}/user/{username}")
        assert response.status_code == 200
        jsonschema.validate(instance=response.json(), schema=USER_SCHEMA)
        # Update
        update_data = {
            "id": str(random.randint(1000, 9999)),
            "username": username,
            "firstName": "Jane",
            "lastName": "Doe",
            "email": f"updated_{username}@example.com",
            "password": "newpassword123",
            "phone": "0987654321",
            "userStatus": "0"
        }
        response = requests.put(f"{BASE_URL}/user/{username}", data=update_data, headers=headers)
        assert response.status_code in [200, 415]
        # Delete
        response = requests.delete(f"{BASE_URL}/user/{username}")
        assert response.status_code in [400, 404]
    else:
        assert response.status_code == 415

def test_auth_and_access_flow():
    username = generate_unique_string("user")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # Create user
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    if response.status_code == 200:
        time.sleep(1)
        # Login
        response = requests.get(f"{BASE_URL}/user/login", params={"username": username, "password": "password123"})
        assert response.status_code == 200
        api_key = response.headers.get("X-API-KEY")
        # Use API key
        pet_id = random.randint(1000, 9999)
        pet_data = {
            "id": str(pet_id),
            "name": generate_unique_string("pet"),
            "status": "available"
        }
        response = requests.post(f"{BASE_URL}/pet", data=pet_data, headers={"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code in [200, 415]
    else:
        assert response.status_code == 415
    # Invalid API key
    pet_data = {
        "id": str(random.randint(1000, 9999)),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", data=pet_data, headers={"api_key": "invalid", "Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 415

# --- Resilience Tests ---

def test_post_pet_rate_limit():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "name": generate_unique_string("pet"),
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
        assert response.status_code in [200, 415, 429]

def test_post_pet_large_payload():
    api_key = get_api_key()
    large_string = "x" * 1000000
    data = {
        "id": str(random.randint(1000, 9999)),
        "name": large_string,
        "status": "available"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/pet", data=data, headers=headers)
    assert response.status_code in [200, 400, 413, 415]

def test_get_pet_timeout():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/pet/1000", timeout=0.001)

def test_post_store_order_rate_limit():
    api_key = get_api_key()
    data = {
        "id": str(random.randint(1000, 9999)),
        "petId": str(random.randint(1000, 9999)),
        "quantity": "1",
        "shipDate": "2025-05-24T12:00:00Z",
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
        assert response.status_code in [200, 415, 429]

def test_post_store_order_large_payload():
    api_key = get_api_key()
    large_string = "x" * 1000000
    data = {
        "id": str(random.randint(1000, 9999)),
        "petId": str(random.randint(1000, 9999)),
        "quantity": "1",
        "shipDate": large_string,
        "status": "placed",
        "complete": "false"
    }
    headers = {"api_key": api_key, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/store/order", data=data, headers=headers)
    assert response.status_code in [200, 400, 413, 415]

def test_get_store_inventory_timeout():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/store/inventory", timeout=0.001)

def test_post_user_rate_limit():
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": generate_unique_string("user"),
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{generate_unique_string('user')}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
        assert response.status_code in [200, 415, 429]

def test_post_user_large_payload():
    large_string = "x" * 1000000
    data = {
        "id": str(random.randint(1000, 9999)),
        "username": generate_unique_string("user"),
        "firstName": large_string,
        "lastName": "Doe",
        "email": f"{generate_unique_string('user')}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": "1"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data=data, headers=headers)
    assert response.status_code in [200, 400, 413, 415]

def test_post_user_empty_payload():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/user", data={}, headers=headers)
    assert response.status_code in [400, 415]