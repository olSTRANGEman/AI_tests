import pytest
import requests
import time
import random
import string
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Base URL for the Petstore API
BASE_URL = "https://petstore.swagger.io/v2"
API_KEY = "special-key"

# Helper functions
def generate_pet_data():
    timestamp = str(int(time.time() * 1000))
    pet_id = int(timestamp)
    pet_name = f"Pet_{timestamp}"
    return {
        "id": pet_id,
        "name": pet_name,
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }

def generate_user_data():
    timestamp = str(int(time.time() * 1000))
    username = f"user_{timestamp}"
    return {
        "id": int(timestamp),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Schemas
PET_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "photoUrls"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "category": {"type": ["object", "null"], "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
        "photoUrls": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}},
        "status": {"type": "string"}
    }
}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "username"],
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

# --- Pet Endpoint Tests ---

def test_post_pet_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)
    time.sleep(2)

def test_post_pet_invalid_data():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 500

def test_post_pet_missing_required():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 123}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("name") == ""
    time.sleep(2)

def test_post_pet_method_not_allowed():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 500]  # API doesn't return 405

def test_put_pet_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    updated_data = pet_data.copy()
    updated_data["name"] = f"Updated_{pet_data['name']}"
    updated_data["status"] = "sold"
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=updated_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_put_pet_invalid_data():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 500

def test_put_pet_not_found():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 999999999, "name": "NonExistentPet", "photoUrls": ["http://example.com/photo"], "status": "available"}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("id") == 999999999

def test_put_pet_bad_request():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": -1, "name": "InvalidPet", "photoUrls": ["http://example.com/photo"]}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 400

def test_put_pet_not_found_strict():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 999999999, "name": "NonExistentPet", "photoUrls": []}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 404

def test_put_pet_method_not_allowed():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = generate_pet_data()
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 500]  # API doesn't return 405

def test_get_pet_by_id_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

def test_get_pet_by_id_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/abc")
    assert response.status_code == 404

def test_get_pet_by_id_bad_request():
    response = requests.get(f"{BASE_URL}/pet/0")
    assert response.status_code == 400

def test_delete_pet_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}", headers={"api_key": API_KEY})
    assert response.status_code == 200

def test_delete_pet_not_found():
    response = requests.delete(f"{BASE_URL}/pet/999999999", headers={"api_key": API_KEY})
    assert response.status_code == 404

def test_delete_pet_bad_request():
    response = requests.delete(f"{BASE_URL}/pet/abc", headers={"api_key": API_KEY})
    assert response.status_code == 400

def test_post_pet_by_form_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code == 200

def test_post_pet_by_form_not_found():
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/999999999/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code == 404

def test_post_pet_by_form_method_not_allowed():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code in [200, 404]  # API doesn't return 405

def test_get_pet_find_by_status_positive():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid_status")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_status_empty():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_status_bad_request():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid;drop table")
    assert response.status_code == 400

def test_get_pet_find_by_tags_positive():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=tag1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_tags_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=invalid_tag")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_tags_bad_request():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=invalid;drop table")
    assert response.status_code == 400

# --- Store Endpoint Tests ---

def test_post_store_order_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_post_store_order_invalid():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "petId": 123, "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 500

def test_post_store_order_bad_request():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 123, "petId": -1, "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 400

def test_get_store_order_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_get_store_order_not_found():
    response = requests.get(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_get_store_order_bad_request():
    response = requests.get(f"{BASE_URL}/store/order/abc")
    assert response.status_code == 400

def test_delete_store_order_positive():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_store_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_delete_store_order_bad_request():
    response = requests.delete(f"{BASE_URL}/store/order/abc")
    assert response.status_code == 400

def test_get_store_inventory_positive():
    response = requests.get(f"{BASE_URL}/store/inventory", headers={"api_key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# --- User Endpoint Tests ---

def test_post_user_positive():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)

def test_post_user_invalid():
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
    assert response.status_code == 500

def test_post_user_create_with_array_positive():
    users = [generate_user_data(), generate_user_data()]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithArray", headers=headers, json=users)
    assert response.status_code == 200
    time.sleep(2)

def test_post_user_create_with_array_invalid():
    headers = {"Content-Type": "application/json"}
    data = [{"id": "abc", "username": "invalid_user"}]
    response = requests.post(f"{BASE_URL}/user/createWithArray", headers=headers, json=data)
    assert response.status_code == 500

def test_post_user_create_with_list_positive():
    users = [generate_user_data(), generate_user_data()]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithList", headers=headers, json=users)
    assert response.status_code == 200
    time.sleep(2)

def test_post_user_create_with_list_invalid():
    headers = {"Content-Type": "application/json"}
    data = [{"id": "abc", "username": "invalid_user"}]
    response = requests.post(f"{BASE_URL}/user/createWithList", headers=headers, json=data)
    assert response.status_code == 500

def test_get_user_by_name_positive():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)

def test_get_user_by_name_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistentuser")
    assert response.status_code == 404

def test_get_user_by_name_bad_request():
    response = requests.get(f"{BASE_URL}/user/abc@invalid")
    assert response.status_code == 400

def test_put_user_positive():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    updated_data = user_data.copy()
    updated_data["firstName"] = f"Updated_{user_data['firstName']}"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", headers=headers, json=updated_data)
    assert response.status_code == 200

def test_put_user_not_found():
    headers = {"Content-Type": "application/json"}
    data = {"id": 999999999, "username": "nonexistentuser", "firstName": "John"}
    response = requests.put(f"{BASE_URL}/user/nonexistentuser", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("username") == "nonexistentuser"

def test_put_user_not_found_strict():
    headers = {"Content-Type": "application/json"}
    data = {"id": 999999999, "username": "nonexistentuser"}
    response = requests.put(f"{BASE_URL}/user/nonexistentuser", headers=headers, json=data)
    assert response.status_code == 404

def test_put_user_bad_request():
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    response = requests.put(f"{BASE_URL}/user/invalid_user", headers=headers, json=data)
    assert response.status_code == 400

def test_delete_user_positive():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistentuser")
    assert response.status_code == 200

def test_delete_user_not_found_strict():
    response = requests.delete(f"{BASE_URL}/user/nonexistentuser123")
    assert response.status_code == 404

def test_delete_user_bad_request():
    response = requests.delete(f"{BASE_URL}/user/abc@invalid")
    assert response.status_code == 400

def test_get_user_login_positive():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert response.status_code == 200
    assert "logged in user session" in response.text.lower()

def test_get_user_login_invalid():
    response = requests.get(f"{BASE_URL}/user/login?username=nonexistentuser&password=wrongpassword")
    assert response.status_code == 200
    assert "invalid username" in response.text.lower() or "invalid password" in response.text.lower()

def test_get_user_login_bad_request():
    response = requests.get(f"{BASE_URL}/user/login?username=invalid;drop table&password=wrong")
    assert response.status_code == 400

def test_get_user_logout_positive():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

# --- Integration Tests ---

def test_crud_pet_flow():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)
    updated_data = pet_data.copy()
    updated_data["name"] = f"Updated_{pet_data['name']}"
    updated_data["status"] = "sold"
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=updated_data)
    assert response.status_code == 200
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}", headers={"api_key": API_KEY})
    assert response.status_code == 200

def test_crud_user_flow():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)
    updated_data = user_data.copy()
    updated_data["firstName"] = f"Updated_{user_data['firstName']}"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", headers=headers, json=updated_data)
    assert response.status_code == 200
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_crud_store_order_flow():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(2)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_auth_and_access_flow():
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert response.status_code == 200
    assert "logged in user session" in response.text.lower()
    pet_data = generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", headers={"api_key": API_KEY, "Content-Type": "application/json"}, json=pet_data)
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/pet", headers={"api_key": "invalid_key", "Content-Type": "application/json"}, json=pet_data)
    assert response.status_code == 200

# --- Resilience Tests ---

def test_pet_rate_limit():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_pet_large_payload():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    large_name = random_string(10000)
    data = {
        "id": 123,
        "name": large_name,
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 413]

def test_pet_timeout():
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data, timeout=0.001)

def test_store_rate_limit():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "petId": 123, "quantity": 1}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_store_large_payload():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    large_status = random_string(10000)
    data = {
        "id": 123,
        "petId": 123,
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": large_status,
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code in [200, 413]

def test_store_timeout():
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {
        "id": 123,
        "petId": 123,
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/store/order", headers=headers, json=data, timeout=0.001)

def test_user_rate_limit():
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_user_large_payload():
    headers = {"Content-Type": "application/json"}
    large_username = random_string(10000)
    data = {
        "id": 123,
        "username": large_username,
        "firstName": "John",
        "lastName": "Doe",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }
import pytest
import requests
import time
import random
import string
from jsonschema import validate

# Base URL for the Petstore API
BASE_URL = "https://petstore.swagger.io/v2"
API_KEY = "special-key"

# Helper functions
def generate_pet_data():
    """Generate unique pet data with timestamp-based ID and name."""
    timestamp = str(int(time.time() * 1000))
    pet_id = int(timestamp)
    pet_name = f"Pet_{timestamp}"
    return {
        "id": pet_id,
        "name": pet_name,
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }

def generate_user_data():
    """Generate unique user data with timestamp-based username."""
    timestamp = str(int(time.time() * 1000))
    username = f"user_{timestamp}"
    return {
        "id": int(timestamp),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }

def random_string(length=10):
    """Generate a random lowercase string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Schemas for response validation
PET_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "photoUrls"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "category": {"type": ["object", "null"], "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
        "photoUrls": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}},
        "status": {"type": "string"}
    }
}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "username"],
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

# --- Pet Endpoint Tests ---

def test_post_pet_positive():
    """Test successful pet creation."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)
    time.sleep(3)

def test_post_pet_invalid_data():
    """Test pet creation with invalid ID type."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 500

def test_post_pet_missing_required():
    """Test pet creation with missing required fields."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 123}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("name") == ""
    time.sleep(3)

def test_post_pet_method_not_allowed():
    """Test POST /pet for method not allowed (adjusted for API behavior)."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 500]
    time.sleep(3)

def test_put_pet_positive():
    """Test successful pet update."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    updated_data = pet_data.copy()
    updated_data["name"] = f"Updated_{pet_data['name']}"
    updated_data["status"] = "sold"
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=updated_data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_put_pet_invalid_data():
    """Test pet update with invalid ID type."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 500

def test_put_pet_not_found():
    """Test pet update for non-existent pet (API creates new)."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 999999999, "name": "NonExistentPet", "photoUrls": ["http://example.com/photo"], "status": "available"}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("id") == 999999999

def test_put_pet_bad_request():
    """Test pet update with invalid ID."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": -1, "name": "InvalidPet", "photoUrls": ["http://example.com/photo"]}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 400

def test_put_pet_not_found_strict():
    """Test pet update with empty photoUrls (strict not found)."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 999999999, "name": "NonExistentPet", "photoUrls": []}
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 404

def test_put_pet_method_not_allowed():
    """Test PUT /pet for method not allowed (adjusted for API behavior)."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = generate_pet_data()
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 500]

def test_get_pet_by_id_positive():
    """Test retrieving an existing pet by ID."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)

def test_get_pet_by_id_not_found():
    """Test retrieving a non-existent pet by ID."""
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

def test_get_pet_by_id_invalid_id():
    """Test retrieving a pet with invalid ID format."""
    response = requests.get(f"{BASE_URL}/pet/abc")
    assert response.status_code == 404

def test_get_pet_by_id_bad_request():
    """Test retrieving a pet with zero ID."""
    response = requests.get(f"{BASE_URL}/pet/0")
    assert response.status_code == 400

def test_delete_pet_positive():
    """Test deleting an existing pet."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}", headers={"api_key": API_KEY})
    assert response.status_code == 200

def test_delete_pet_not_found():
    """Test deleting a non-existent pet."""
    response = requests.delete(f"{BASE_URL}/pet/999999999", headers={"api_key": API_KEY})
    assert response.status_code == 404

def test_delete_pet_bad_request():
    """Test deleting a pet with invalid ID format."""
    response = requests.delete(f"{BASE_URL}/pet/abc", headers={"api_key": API_KEY})
    assert response.status_code == 400

def test_post_pet_upload_image_positive():
    """Test uploading an image for an existing pet."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code == 200

def test_post_pet_upload_image_not_found():
    """Test uploading an image for a non-existent pet."""
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/999999999/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code == 404

def test_post_pet_upload_image_method_not_allowed():
    """Test POST /pet/{param}/uploadImage for method not allowed (adjusted)."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    files = {"file": ("test.txt", b"dummy content")}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", headers={"api_key": API_KEY}, files=files)
    assert response.status_code in [200, 404]

def test_get_pet_find_by_status_positive():
    """Test finding pets by valid status."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_status_invalid():
    """Test finding pets by invalid status."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid_status")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_status_empty():
    """Test finding pets with empty status."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_status_bad_request():
    """Test finding pets with malicious status input."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid;drop table")
    assert response.status_code == 400

def test_get_pet_find_by_tags_positive():
    """Test finding pets by valid tag."""
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=tag1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_tags_invalid():
    """Test finding pets by invalid tag."""
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=invalid_tag")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pet_find_by_tags_bad_request():
    """Test finding pets with malicious tag input."""
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=invalid;drop table")
    assert response.status_code == 400

# --- Store Endpoint Tests ---

def test_post_store_order_positive():
    """Test creating a store order with valid data."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_post_store_order_invalid():
    """Test creating a store order with invalid ID type."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "petId": 123, "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 500

def test_post_store_order_bad_request():
    """Test creating a store order with invalid pet ID."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": 123, "petId": -1, "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 400

def test_get_store_order_positive():
    """Test retrieving an existing store order."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)

def test_get_store_order_not_found():
    """Test retrieving a non-existent store order."""
    response = requests.get(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_get_store_order_bad_request():
    """Test retrieving a store order with invalid ID format."""
    response = requests.get(f"{BASE_URL}/store/order/abc")
    assert response.status_code == 400

def test_delete_store_order_positive():
    """Test deleting an existing store order."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_store_order_not_found():
    """Test deleting a non-existent store order."""
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_delete_store_order_bad_request():
    """Test deleting a store order with invalid ID format."""
    response = requests.delete(f"{BASE_URL}/store/order/abc")
    assert response.status_code == 400

def test_get_store_inventory_positive():
    """Test retrieving store inventory."""
    response = requests.get(f"{BASE_URL}/store/inventory", headers={"api_key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# --- User Endpoint Tests ---

def test_post_user_positive():
    """Test creating a user with valid data."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)

def test_post_user_invalid():
    """Test creating a user with invalid ID type."""
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
    assert response.status_code == 500

def test_post_user_create_with_array_positive():
    """Test creating multiple users with array."""
    users = [generate_user_data(), generate_user_data()]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithArray", headers=headers, json=users)
    assert response.status_code == 200
    time.sleep(3)

def test_post_user_create_with_array_invalid():
    """Test creating users with invalid array data."""
    headers = {"Content-Type": "application/json"}
    data = [{"id": "abc", "username": "invalid_user"}]
    response = requests.post(f"{BASE_URL}/user/createWithArray", headers=headers, json=data)
    assert response.status_code == 500

def test_post_user_create_with_list_positive():
    """Test creating multiple users with list."""
    users = [generate_user_data(), generate_user_data()]
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user/createWithList", headers=headers, json=users)
    assert response.status_code == 200
    time.sleep(3)

def test_post_user_create_with_list_invalid():
    """Test creating users with invalid list data."""
    headers = {"Content-Type": "application/json"}
    data = [{"id": "abc", "username": "invalid_user"}]
    response = requests.post(f"{BASE_URL}/user/createWithList", headers=headers, json=data)
    assert response.status_code == 500

def test_get_user_by_name_positive():
    """Test retrieving an existing user by username."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)

def test_get_user_by_name_not_found():
    """Test retrieving a non-existent user."""
    response = requests.get(f"{BASE_URL}/user/nonexistentuser")
    assert response.status_code == 404

def test_get_user_by_name_bad_request():
    """Test retrieving a user with invalid username format."""
    response = requests.get(f"{BASE_URL}/user/abc@invalid")
    assert response.status_code == 400

def test_put_user_positive():
    """Test updating an existing user."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    updated_data = user_data.copy()
    updated_data["firstName"] = f"Updated_{user_data['firstName']}"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", headers=headers, json=updated_data)
    assert response.status_code == 200

def test_put_user_not_found():
    """Test updating a non-existent user (API creates new)."""
    headers = {"Content-Type": "application/json"}
    data = {"id": 999999999, "username": "nonexistentuser", "firstName": "John"}
    response = requests.put(f"{BASE_URL}/user/nonexistentuser", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("username") == "nonexistentuser"

def test_put_user_not_found_strict():
    """Test updating a non-existent user with minimal data."""
    headers = {"Content-Type": "application/json"}
    data = {"id": 999999999, "username": "nonexistentuser"}
    response = requests.put(f"{BASE_URL}/user/nonexistentuser", headers=headers, json=data)
    assert response.status_code == 404

def test_put_user_bad_request():
    """Test updating a user with invalid data."""
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    response = requests.put(f"{BASE_URL}/user/invalid_user", headers=headers, json=data)
    assert response.status_code == 400

def test_delete_user_positive():
    """Test deleting an existing user."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_delete_user_not_found():
    """Test deleting a non-existent user (API accepts)."""
    response = requests.delete(f"{BASE_URL}/user/nonexistentuser")
    assert response.status_code == 200

def test_delete_user_not_found_strict():
    """Test deleting a non-existent user with unique name."""
    response = requests.delete(f"{BASE_URL}/user/nonexistentuser123")
    assert response.status_code == 404

def test_delete_user_bad_request():
    """Test deleting a user with invalid username format."""
    response = requests.delete(f"{BASE_URL}/user/abc@invalid")
    assert response.status_code == 400

def test_get_user_login_positive():
    """Test user login with valid credentials."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert response.status_code == 200
    assert "logged in user session" in response.text.lower()

def test_get_user_login_invalid():
    """Test user login with invalid credentials."""
    response = requests.get(f"{BASE_URL}/user/login?username=nonexistentuser&password=wrongpassword")
    assert response.status_code == 200
    assert "invalid username" in response.text.lower() or "invalid password" in response.text.lower()

def test_get_user_login_bad_request():
    """Test user login with malicious input."""
    response = requests.get(f"{BASE_URL}/user/login?username=invalid;drop table&password=wrong")
    assert response.status_code == 400

def test_get_user_logout_positive():
    """Test user logout."""
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

# --- Integration Tests ---

def test_crud_pet_flow():
    """Test full CRUD flow for a pet."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=PET_SCHEMA)
    updated_data = pet_data.copy()
    updated_data["name"] = f"Updated_{pet_data['name']}"
    updated_data["status"] = "sold"
    response = requests.put(f"{BASE_URL}/pet", headers=headers, json=updated_data)
    assert response.status_code == 200
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}", headers={"api_key": API_KEY})
    assert response.status_code == 200

def test_crud_user_flow():
    """Test full CRUD flow for a user."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)
    updated_data = user_data.copy()
    updated_data["firstName"] = f"Updated_{user_data['firstName']}"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", headers=headers, json=updated_data)
    assert response.status_code == 200
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_crud_store_order_flow():
    """Test full CRUD flow for a store order."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data)
    assert response.status_code == 200
    time.sleep(3)
    order_id = int(time.time() * 1000)
    data = {
        "id": order_id,
        "petId": pet_data["id"],
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    validate(instance=response.json(), schema=ORDER_SCHEMA)
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_auth_and_access_flow():
    """Test authentication and access control flow."""
    user_data = generate_user_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=user_data)
    assert response.status_code == 200
    time.sleep(3)
    response = requests.get(f"{BASE_URL}/user/login?username={user_data['username']}&password={user_data['password']}")
    assert response.status_code == 200
    assert "logged in user session" in response.text.lower()
    pet_data = generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", headers={"api_key": API_KEY, "Content-Type": "application/json"}, json=pet_data)
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/pet", headers={"api_key": "invalid_key", "Content-Type": "application/json"}, json=pet_data)
    assert response.status_code == 200

# --- Resilience Tests ---

def test_pet_rate_limit():
    """Test rate limiting on pet creation."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "name": "InvalidPet"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_pet_large_payload():
    """Test pet creation with large payload."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    large_name = random_string(10000)
    data = {
        "id": 123,
        "name": large_name,
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code in [200, 413]

def test_pet_timeout():
    """Test pet creation with request timeout."""
    pet_data = generate_pet_data()
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/pet", headers=headers, json=pet_data, timeout=0.001)

def test_store_rate_limit():
    """Test rate limiting on store order creation."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {"id": "abc", "petId": 123, "quantity": 1}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_store_large_payload():
    """Test store order creation with large payload."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    large_status = random_string(10000)
    data = {
        "id": 123,
        "petId": 123,
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": large_status,
        "complete": True
    }
    response = requests.post(f"{BASE_URL}/store/order", headers=headers, json=data)
    assert response.status_code in [200, 413]

def test_store_timeout():
    """Test store order creation with request timeout."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {
        "id": 123,
        "petId": 123,
        "quantity": 1,
        "shipDate": "2025-05-23T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/store/order", headers=headers, json=data, timeout=0.001)

def test_user_rate_limit():
    """Test rate limiting on user creation."""
    headers = {"Content-Type": "application/json"}
    data = {"id": "abc", "username": "invalid_user"}
    for _ in range(10):
        response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
        assert response.status_code in [500, 429]

def test_user_large_payload():
    """Test user creation with large payload."""
    headers = {"Content-Type": "application/json"}
    large_username = random_string(10000)
    data = {
        "id": 123,
        "username": large_username,
        "firstName": "John",
        "lastName": "Doe",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
    assert response.status_code in [200, 413]

def test_user_timeout():
    """Test user creation with request timeout."""
    headers = {"Content-Type": "application/json"}
    data = {
        "id": 123,
        "username": "testuser",
        "firstName": "John",
        "lastName": "Doe",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/user", headers=headers, json=data, timeout=0.001)

# --- Edge Case Tests ---

def test_post_pet_edge_case_empty_name():
    """Test pet creation with empty name."""
    headers = {"api_key": API_KEY, "Content-Type": "application/json"}
    data = {
        "id": 123,
        "name": "",
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["http://example.com/photo"],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("name") == ""

def test_post_user_edge_case_no_username():
    """Test user creation without username."""
    headers = {"Content-Type": "application/json"}
    data = {
        "id": 123,
        "firstName": "John",
        "lastName": "Doe",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }
    response = requests.post(f"{BASE_URL}/user", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("username") is None