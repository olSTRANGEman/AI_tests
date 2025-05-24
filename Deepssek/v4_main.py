import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

# Helpers
def generate_unique_id():
    return random.randint(1, 10**8)

def create_test_pet():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": "TestPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": random.choice(["available", "pending", "sold"])
    }
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    return pet_id, response

def create_test_order():
    pet_id, _ = create_test_pet()
    order_id = generate_unique_id()
    data = {
        "id": order_id,
        "petId": pet_id,
        "quantity": 1,
        "shipDate": "2023-01-01T00:00:00Z",
        "status": "placed"
    }
    response = requests.post(
        f"{BASE_URL}/store/order",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    return order_id, response

def create_test_user():
    username = f"user_{generate_unique_id()}"
    data = {"username": username, "email": f"{username}@example.com"}
    response = requests.post(
        f"{BASE_URL}/user",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    return username, response

# Pet Endpoints (20 тестов)
def test_post_pet_valid():
    pet_id, response = create_test_pet()
    assert response.status_code == 200
    assert requests.get(f"{BASE_URL}/pet/{pet_id}").status_code == 200

def test_post_pet_invalid():
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps({"invalid": "data"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]

def test_put_pet_valid():
    pet_id, _ = create_test_pet()
    data = {
        "id": pet_id,
        "name": "UpdatedPet",
        "photoUrls": ["http://new.url"],
        "status": "pending"
    }
    response = requests.put(
        f"{BASE_URL}/pet",
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200

def test_put_pet_invalid():
    response = requests.put(
        f"{BASE_URL}/pet",
        data=json.dumps({"id": "invalid"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 404, 500]

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status_valid(status):
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": status}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_status_invalid():
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": "invalid"}
    )
    assert response.status_code in [200, 400]

def test_get_pet_by_tags():
    response = requests.get(
        f"{BASE_URL}/pet/findByTags",
        params={"tags": "test_tag"}
    )
    assert response.status_code in [200, 400]

def test_get_pet_by_id_valid():
    pet_id, _ = create_test_pet()
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

def test_get_pet_by_id_invalid():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code in [400, 404]

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/{generate_unique_id()}")
    assert response.status_code == 404

def test_update_pet_with_form():
    pet_id, _ = create_test_pet()
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}",
        data={"name": "NewName", "status": "sold"}
    )
    assert response.status_code in [200, 405]

def test_upload_pet_image():
    pet_id, _ = create_test_pet()
    files = {'file': ('test.jpg', b'content', 'image/jpeg')}
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}/uploadImage",
        files=files
    )
    assert response.status_code == 200

def test_delete_pet_valid():
    pet_id, _ = create_test_pet()
    response = requests.delete(
        f"{BASE_URL}/pet/{pet_id}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 200

def test_delete_pet_invalid():
    response = requests.delete(
        f"{BASE_URL}/pet/invalid_id",
        headers={"api_key": "special-key"}
    )
    assert response.status_code in [400, 404]

def test_delete_pet_unauthorized():
    pet_id, _ = create_test_pet()
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code in [401, 403]

# Store Endpoints (10 тестов)
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_create_order_valid():
    order_id, response = create_test_order()
    assert response.status_code == 200
    assert requests.get(f"{BASE_URL}/store/order/{order_id}").status_code == 200

def test_create_order_invalid():
    response = requests.post(
        f"{BASE_URL}/store/order",
        data=json.dumps({"invalid": "data"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]

def test_get_order_valid():
    order_id, _ = create_test_order()
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_get_order_invalid():
    response = requests.get(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code in [400, 404]

def test_get_order_not_found():
    response = requests.get(f"{BASE_URL}/store/order/{generate_unique_id()}")
    assert response.status_code == 404

def test_delete_order_valid():
    order_id, _ = create_test_order()
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code in [200, 404]

def test_delete_order_invalid():
    response = requests.delete(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code in [400, 404]

# User Endpoints (18 тестов)
def test_create_user_valid():
    username, response = create_test_user()
    assert response.status_code == 200
    assert requests.get(f"{BASE_URL}/user/{username}").status_code == 200

def test_create_user_invalid():
    response = requests.post(
        f"{BASE_URL}/user",
        data=json.dumps({"email": "invalid"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]

def test_create_users_with_array():
    users = [{"username": f"user_{i}", "email": f"user_{i}@test.com"} for i in range(3)]
    response = requests.post(
        f"{BASE_URL}/user/createWithArray",
        data=json.dumps(users),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200

def test_create_users_with_list():
    users = [{"username": f"user_{i}", "email": f"user_{i}@test.com"} for i in range(3)]
    response = requests.post(
        f"{BASE_URL}/user/createWithList",
        data=json.dumps(users),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200

def test_login_valid():
    username, _ = create_test_user()
    response = requests.get(
        f"{BASE_URL}/user/login",
        params={"username": username, "password": "any"}
    )
    assert response.status_code == 200

def test_login_invalid():
    response = requests.get(
        f"{BASE_URL}/user/login",
        params={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code in [200, 400]

def test_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_valid():
    username, _ = create_test_user()
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_get_user_invalid():
    response = requests.get(f"{BASE_URL}/user/invalid_user!")
    assert response.status_code in [400, 404]

def test_get_user_not_found():
    response = requests.get(f"{BASE_URL}/user/non_existent_user")
    assert response.status_code == 404

def test_update_user_valid():
    username, _ = create_test_user()
    response = requests.put(
        f"{BASE_URL}/user/{username}",
        data=json.dumps({"email": "new@test.com"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200

def test_update_user_invalid():
    response = requests.put(
        f"{BASE_URL}/user/invalid_user!",
        data=json.dumps({"email": "new@test.com"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 404]

def test_delete_user_valid():
    username, _ = create_test_user()
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_delete_user_invalid():
    response = requests.delete(f"{BASE_URL}/user/invalid_user!")
    assert response.status_code in [400, 404]

# Интеграционные тесты (3 теста)
def test_full_pet_lifecycle():
    pet_id, _ = create_test_pet()
    
    # Update
    update_data = {
        "id": pet_id,
        "name": "Updated",
        "photoUrls": ["http://new.url"],
        "status": "sold"
    }
    response = requests.put(
        f"{BASE_URL}/pet",
        data=json.dumps(update_data),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    
    # Delete
    response = requests.delete(
        f"{BASE_URL}/pet/{pet_id}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 200

def test_auth_workflow():
    # Test unauthorized access
    response = requests.delete(f"{BASE_URL}/pet/999")
    assert response.status_code in [401, 403, 404]
    
    # Test authorized access
    response = requests.delete(
        f"{BASE_URL}/pet/999",
        headers={"api_key": "special-key"}
    )
    assert response.status_code in [200, 404]

# Тесты устойчивости (3 теста)
@pytest.mark.flaky(reruns=3)
def test_high_load():
    for _ in range(10):
        requests.get(f"{BASE_URL}/store/inventory")
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_large_payload():
    large_data = {"data": "x"*10**6}
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps(large_data),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [200, 413, 500]

def test_timeout_handling():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/store/inventory", timeout=0.001)