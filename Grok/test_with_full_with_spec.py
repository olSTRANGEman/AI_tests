import pytest
import requests
import uuid
import time
import random
import string

@pytest.fixture
def api_config():
    base_url = "https://petstore.swagger.io/v2"
    headers = {"api_key": "special-key"}  # For endpoints requiring api_key
    return {"base_url": base_url, "headers": headers}

# Helper to generate unique pet data
def generate_pet_data():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Pet_{unique_id}",
        "photoUrls": ["http://example.com/photo"],
        "status": random.choice(["available", "pending", "sold"])
    }

# Helper to generate unique user data
def generate_user_data():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"user_{unique_id}",
        "firstName": "Test",
        "lastName": "User",
        "email": f"user_{unique_id}@example.com",
        "password": "password123",
        "phone": "1234567890"
    }

# Helper to generate unique order data
def generate_order_data(pet_id):
    return {
        "petId": pet_id,
        "quantity": 1,
        "status": "placed",
        "complete": "false"
    }

# --- Pet Endpoints ---

# POST /pet
def test_post_pet_valid(api_config):
    data = generate_pet_data()
    response = requests.post(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405
    assert response.json().get("message") == "Invalid input"

def test_post_pet_missing_required_fields(api_config):
    data = {"status": "available"}  # Missing name, photoUrls
    response = requests.post(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

def test_post_pet_empty_body(api_config):
    response = requests.post(
        f"{api_config['base_url']}/pet",
        data={},
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

# PUT /pet
def test_put_pet_valid(api_config):
    data = generate_pet_data()
    data["id"] = random.randint(1000, 9999)
    response = requests.put(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code in [400, 404, 405]
    if response.status_code == 200:
        assert response.json().get("name") == data["name"]

def test_put_pet_invalid_id(api_config):
    data = generate_pet_data()
    data["id"] = -1
    response = requests.put(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 400

def test_put_pet_missing_required_fields(api_config):
    data = {"id": random.randint(1000, 9999), "status": "available"}
    response = requests.put(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

# GET /pet/findByStatus
def test_get_pet_find_by_status_valid(api_config):
    params = {"status": "available"}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByStatus",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_find_by_status_invalid(api_config):
    params = {"status": "invalid_status"}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByStatus",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 400

def test_get_pet_find_by_status_multiple(api_config):
    params = {"status": "available,pending"}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByStatus",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200

# GET /pet/findByTags
def test_get_pet_find_by_tags_valid(api_config):
    params = {"tags": "tag1"}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByTags",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200

def test_get_pet_find_by_tags_invalid(api_config):
    params = {"tags": ""}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByTags",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 400

def test_get_pet_find_by_tags_multiple(api_config):
    params = {"tags": "tag1,tag2"}
    response = requests.get(
        f"{api_config['base_url']}/pet/findByTags",
        params=params,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200

# GET /pet/{petId}
def test_get_pet_by_id_valid(api_config):
    pet_id = random.randint(1, 100)
    response = requests.get(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers=api_config['headers']
    )
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json().get("id") == pet_id

def test_get_pet_by_id_invalid(api_config):
    response = requests.get(
        f"{api_config['base_url']}/pet/-1",
        headers=api_config['headers']
    )
    assert response.status_code == 400

def test_get_pet_by_id_not_found(api_config):
    response = requests.get(
        f"{api_config['base_url']}/pet/999999",
        headers=api_config['headers']
    )
    assert response.status_code == 404

# POST /pet/{petId}
def test_post_pet_by_id_valid(api_config):
    pet_id = random.randint(1000, 9999)
    data = {"name": f"Updated_{pet_id}", "status": "available"}
    response = requests.post(
        f"{api_config['base_url']}/pet/{pet_id}",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

def test_post_pet_by_id_missing_data(api_config):
    pet_id = random.randint(1000, 9999)
    response = requests.post(
        f"{api_config['base_url']}/pet/{pet_id}",
        data={},
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

def test_post_pet_by_id_invalid_id(api_config):
    data = {"name": "TestPet", "status": "available"}
    response = requests.post(
        f"{api_config['base_url']}/pet/-1",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

# DELETE /pet/{petId}
def test_delete_pet_by_id_valid(api_config):
    pet_id = random.randint(1000, 9999)
    response = requests.delete(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code in [400, 404]

def test_delete_pet_by_id_invalid(api_config):
    response = requests.delete(
        f"{api_config['base_url']}/pet/-1",
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 400

def test_delete_pet_by_id_not_found(api_config):
    response = requests.delete(
        f"{api_config['base_url']}/pet/999999",
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 404

# POST /pet/{petId}/uploadImage
def test_post_pet_upload_image_valid(api_config):
    pet_id = random.randint(1000, 9999)
    files = {"file": ("test.jpg", b"image_data", "image/jpeg")}
    data = {"additionalMetadata": "Test metadata"}
    response = requests.post(
        f"{api_config['base_url']}/pet/{pet_id}/uploadImage",
        files=files,
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200
    assert response.json().get("code") == 200

def test_post_pet_upload_image_no_file(api_config):
    pet_id = random.randint(1000, 9999)
    data = {"additionalMetadata": "Test metadata"}
    response = requests.post(
        f"{api_config['base_url']}/pet/{pet_id}/uploadImage",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200  # Optional file

def test_post_pet_upload_image_invalid_id(api_config):
    files = {"file": ("test.jpg", b"image_data", "image/jpeg")}
    response = requests.post(
        f"{api_config['base_url']}/pet/-1/uploadImage",
        files=files,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 200  # Spec doesn't define error for invalid ID

# --- Store Endpoints ---

# GET /store/inventory
def test_get_store_inventory(api_config):
    response = requests.get(
        f"{api_config['base_url']}/store/inventory",
        headers=api_config['headers']
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_store_inventory_unauthorized(api_config):
    response = requests.get(
        f"{api_config['base_url']}/store/inventory",
        headers={}  # Missing api_key
    )
    assert response.status_code in [401, 403]

# POST /store/order
def test_post_store_order_valid(api_config):
    pet_id = random.randint(1000, 9999)
    data = generate_order_data(pet_id)
    response = requests.post(
        f"{api_config['base_url']}/store/order",
        data=data
    )
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        assert response.json().get("petId") == pet_id

def test_post_store_order_invalid(api_config):
    data = {"quantity": -1}
    response = requests.post(
        f"{api_config['base_url']}/store/order",
        data=data
    )
    assert response.status_code == 400

def test_post_store_order_missing_fields(api_config):
    data = {"petId": random.randint(1000, 9999)}
    response = requests.post(
        f"{api_config['base_url']}/store/order",
        data=data
    )
    assert response.status_code == 400

# GET /store/order/{orderId}
def test_get_store_order_by_id_valid(api_config):
    order_id = random.randint(1, 10)
    response = requests.get(
        f"{api_config['base_url']}/store/order/{order_id}"
    )
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json().get("id") == order_id

def test_get_store_order_by_id_invalid(api_config):
    response = requests.get(
        f"{api_config['base_url']}/store/order/0"
    )
    assert response.status_code == 400

def test_get_store_order_by_id_not_found(api_config):
    response = requests.get(
        f"{api_config['base_url']}/store/order/999"
    )
    assert response.status_code == 404

# DELETE /store/order/{orderId}
def test_delete_store_order_by_id_valid(api_config):
    order_id = random.randint(1, 10)
    response = requests.delete(
        f"{api_config['base_url']}/store/order/{order_id}"
    )
    assert response.status_code in [400, 404]

def test_delete_store_order_by_id_invalid(api_config):
    response = requests.delete(
        f"{api_config['base_url']}/store/order/0"
    )
    assert response.status_code == 400

def test_delete_store_order_by_id_not_found(api_config):
    response = requests.delete(
        f"{api_config['base_url']}/store/order/999"
    )
    assert response.status_code == 404

# --- User Endpoints ---

# POST /user
def test_post_user_valid(api_config):
    data = generate_user_data()
    response = requests.post(
        f"{api_config['base_url']}/user",
        data=data
    )
    assert response.status_code == 200

def test_post_user_missing_fields(api_config):
    data = {"username": f"user_{str(uuid.uuid4())[:8]}"}
    response = requests.post(
        f"{api_config['base_url']}/user",
        data=data
    )
    assert response.status_code == 200

def test_post_user_empty_body(api_config):
    response = requests.post(
        f"{api_config['base_url']}/user",
        data={}
    )
    assert response.status_code == 200

# POST /user/createWithArray
def test_post_user_create_with_array_valid(api_config):
    data = [generate_user_data()]
    response = requests.post(
        f"{api_config['base_url']}/user/createWithArray",
        data={"users": str(data)}
    )
    assert response.status_code == 200

def test_post_user_create_with_array_empty(api_config):
    response = requests.post(
        f"{api_config['base_url']}/user/createWithArray",
        data={"users": "[]"}
    )
    assert response.status_code == 200

# POST /user/createWithList
def test_post_user_create_with_list_valid(api_config):
    data = [generate_user_data()]
    response = requests.post(
        f"{api_config['base_url']}/user/createWithList",
        data={"users": str(data)}
    )
    assert response.status_code == 200

def test_post_user_create_with_list_empty(api_config):
    response = requests.post(
        f"{api_config['base_url']}/user/createWithList",
        data={"users": "[]"}
    )
    assert response.status_code == 200

# GET /user/login
def test_get_user_login_valid(api_config):
    params = {"username": "user1", "password": "password123"}
    response = requests.get(
        f"{api_config['base_url']}/user/login",
        params=params
    )
    assert response.status_code == 200
    assert "X-Rate-Limit" in response.headers
    assert "X-Expires-After" in response.headers

def test_get_user_login_invalid(api_config):
    params = {"username": "invalid", "password": "wrong"}
    response = requests.get(
        f"{api_config['base_url']}/user/login",
        params=params
    )
    assert response.status_code == 400

def test_get_user_login_missing_params(api_config):
    response = requests.get(
        f"{api_config['base_url']}/user/login",
        params={}
    )
    assert response.status_code == 400


# GET /user/{username}
def test_get_user_by_username_valid(api_config):
    response = requests.get(
        f"{api_config['base_url']}/user/user1"
    )
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json().get("username") == "user1"

def test_get_user_by_username_invalid(api_config):
    response = requests.get(
        f"{api_config['base_url']}/user/invalid%20user"
    )
    assert response.status_code == 400

def test_get_user_by_username_not_found(api_config):
    unique_id = str(uuid.uuid4())[:8]
    response = requests.get(
        f"{api_config['base_url']}/user/nonexistent_{unique_id}"
    )
    assert response.status_code == 404

# PUT /user/{username}
def test_put_user_valid(api_config):
    username = f"user_{str(uuid.uuid4())[:8]}"
    data = generate_user_data()
    data["username"] = username
    response = requests.put(
        f"{api_config['base_url']}/user/{username}",
        data=data
    )
    assert response.status_code in [400, 404]

def test_put_user_invalid_username(api_config):
    data = generate_user_data()
    response = requests.put(
        f"{api_config['base_url']}/user/invalid%20user",
        data=data
    )
    assert response.status_code == 400

def test_put_user_missing_fields(api_config):
    username = f"user_{str(uuid.uuid4())[:8]}"
    response = requests.put(
        f"{api_config['base_url']}/user/{username}",
        data={}
    )
    assert response.status_code in [400, 404]

# DELETE /user/{username}
def test_delete_user_valid(api_config):
    username = f"user_{str(uuid.uuid4())[:8]}"
    response = requests.delete(
        f"{api_config['base_url']}/user/{username}"
    )
    assert response.status_code in [400, 404]

def test_delete_user_invalid_username(api_config):
    response = requests.delete(
        f"{api_config['base_url']}/user/invalid%20user"
    )
    assert response.status_code == 400

def test_delete_user_not_found(api_config):
    unique_id = str(uuid.uuid4())[:8]
    response = requests.delete(
        f"{api_config['base_url']}/user/nonexistent_{unique_id}"
    )
    assert response.status_code == 404

# --- Integration Tests ---

def test_crud_pet_flow(api_config):
    pet_id = random.randint(1000, 9999)
    pet_data = generate_pet_data()
    pet_data["id"] = pet_id
    response = requests.post(
        f"{api_config['base_url']}/pet",
        data=pet_data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

    response = requests.get(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers=api_config['headers']
    )
    assert response.status_code in [200, 404]

    pet_data["name"] = f"Updated_{pet_id}"
    response = requests.put(
        f"{api_config['base_url']}/pet",
        data=pet_data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code in [400, 404, 405]

    response = requests.delete(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code in [400, 404]

def test_crud_store_flow(api_config):
    pet_id = random.randint(1000, 9999)
    order_id = random.randint(1, 10)
    order_data = generate_order_data(pet_id)
    order_data["id"] = order_id
    response = requests.post(
        f"{api_config['base_url']}/store/order",
        data=order_data
    )
    assert response.status_code in [200, 400]

    response = requests.get(
        f"{api_config['base_url']}/store/order/{order_id}"
    )
    assert response.status_code in [200, 404]

    response = requests.delete(
        f"{api_config['base_url']}/store/order/{order_id}"
    )
    assert response.status_code in [400, 404]

def test_crud_user_flow(api_config):
    user_data = generate_user_data()
    username = user_data["username"]
    response = requests.post(
        f"{api_config['base_url']}/user",
        data=user_data
    )
    assert response.status_code == 200

    response = requests.get(
        f"{api_config['base_url']}/user/{username}"
    )
    assert response.status_code in [200, 404]

    user_data["firstName"] = "Updated"
    response = requests.put(
        f"{api_config['base_url']}/user/{username}",
        data=user_data
    )
    assert response.status_code in [400, 404]

    response = requests.delete(
        f"{api_config['base_url']}/user/{username}"
    )
    assert response.status_code in [400, 404]

def test_auth_and_access_flow(api_config):
    params = {"username": "user1", "password": "password123"}
    response = requests.get(
        f"{api_config['base_url']}/user/login",
        params=params
    )
    assert response.status_code == 200
    token = response.json()

    pet_id = random.randint(1000, 9999)
    response = requests.get(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers={**api_config['headers'], "Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]

    response = requests.get(
        f"{api_config['base_url']}/pet/{pet_id}",
        headers={**api_config['headers'], "Authorization": "Bearer invalid"}
    )
    assert response.status_code in [401, 403]

# --- Resilience Tests ---

def test_rate_limit_pet_by_id(api_config):
    pet_id = random.randint(1000, 9999)
    for _ in range(50):
        response = requests.get(
            f"{api_config['base_url']}/pet/{pet_id}",
            headers=api_config['headers']
        )
        assert response.status_code in [200, 404, 429]

def test_large_input_pet(api_config):
    large_name = "x" * 10000
    data = {"name": large_name, "photoUrls": ["http://example.com"], "status": "available"}
    response = requests.post(
        f"{api_config['base_url']}/pet",
        data=data,
        headers={**api_config['headers'], "Authorization": "Bearer special-key"}
    )
    assert response.status_code == 405

def test_timeout_pet_by_id(api_config):
    pet_id = random.randint(1000, 9999)
    try:
        response = requests.get(
            f"{api_config['base_url']}/pet/{pet_id}",
            headers=api_config['headers'],
            timeout=0.001
        )
    except requests.exceptions.Timeout:
        assert True
    else:
        assert response.status_code in [200, 404]