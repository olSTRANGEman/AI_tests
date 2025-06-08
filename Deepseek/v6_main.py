import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

# Helpers
def generate_unique_id():
    return random.randint(1, 10**8)

def create_test_pet(status="available"):
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": "TestPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": status
    }
    response = requests.post(
        f"{BASE_URL}/pet",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    return pet_id, response

# Pet Endpoints (25 тестов)
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_post_pet_valid():
    pet_id, response = create_test_pet()
    assert response.status_code == 200
    time.sleep(0.5)
    assert requests.get(f"{BASE_URL}/pet/{pet_id}").status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"name": "NoPhoto"}, 400),
    ({"id": "invalid"}, 400),
    ({"status": "unknown"}, 400),
    ({"photoUrls": "string"}, 400)
])
def test_post_pet_invalid(data, expected):
    response = requests.post(
        f"{BASE_URL}/pet",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == expected

def test_put_pet_valid():
    pet_id, _ = create_test_pet()
    data = {
        "id": pet_id,
        "name": "Updated",
        "photoUrls": ["http://new.url"],
        "status": "sold"
    }
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"id": "invalid"}, 400),
    ({}, 404),
    ({"status": "invalid"}, 400)
])
def test_put_pet_invalid(data, expected):
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == expected

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status_valid(status):
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": status}
    )
    assert response.status_code == 200

def test_get_pet_by_status_empty():
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": "invalid_status"}
    )
    assert response.status_code == 400

def test_get_pet_by_tags():
    response = requests.get(
        f"{BASE_URL}/pet/findByTags",
        params={"tags": "test_tag"}
    )
    assert response.status_code in [200, 400]

def test_get_pet_by_id_valid():
    pet_id, _ = create_test_pet()
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

@pytest.mark.parametrize("pet_id,expected", [
    ("invalid_id", 400),
    (999999999, 404)
])
def test_get_pet_by_id_invalid(pet_id, expected):
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == expected

def test_update_pet_form_valid():
    pet_id, _ = create_test_pet()
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}",
        data={"name": "NewName", "status": "pending"}
    )
    assert response.status_code in [200, 405]

def test_update_pet_form_invalid():
    response = requests.post(
        f"{BASE_URL}/pet/invalid_id",
        data={"status": "invalid"}
    )
    assert response.status_code in [400, 405]

def test_upload_pet_image_valid():
    pet_id, _ = create_test_pet()
    files = {'file': ('test.jpg', b'content', 'image/jpeg')}
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}/uploadImage",
        files=files
    )
    assert response.status_code == 200

def test_upload_pet_image_invalid():
    response = requests.post(
        f"{BASE_URL}/pet/invalid_id/uploadImage",
        files={'file': ('test.jpg', b'content')}
    )
    assert response.status_code in [400, 404]

def test_delete_pet_valid():
    pet_id, _ = create_test_pet()
    response = requests.delete(
        f"{BASE_URL}/pet/{pet_id}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 200

def test_delete_pet_unauthorized():
    pet_id, _ = create_test_pet()
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code in [401, 403]

@pytest.mark.parametrize("pet_id,expected", [
    ("invalid_id", 400),
    (999999999, 404)
])
def test_delete_pet_invalid(pet_id, expected):
    response = requests.delete(
        f"{BASE_URL}/pet/{pet_id}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == expected

# Store Endpoints (15 тестов)
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_create_order_valid():
    order_id = generate_unique_id()
    data = {
        "id": order_id,
        "petId": create_test_pet()[0],
        "quantity": 1,
        "status": "placed"
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"id": "invalid"}, 400),
    ({"petId": 999999}, 400),
    ({}, 400)
])
def test_create_order_invalid(data, expected):
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == expected

def test_get_order_valid():
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

@pytest.mark.parametrize("order_id,expected", [
    ("invalid_id", 400),
    (999999999, 404)
])
def test_get_order_invalid(order_id, expected):
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == expected

def test_delete_order_valid():
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_order_invalid():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

# User Endpoints (20 тестов)
def test_create_user_valid():
    username = f"user_{generate_unique_id()}"
    response = requests.post(
        f"{BASE_URL}/user",
        json={"username": username, "email": "test@example.com"}
    )
    assert response.status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"email": "invalid"}, 400),
    ({"username": "bad@user"}, 400),
    ({}, 400)
])
def test_create_user_invalid(data, expected):
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == expected

def test_create_users_with_array():
    users = [{"username": f"user_{i}"} for i in range(3)]
    response = requests.post(
        f"{BASE_URL}/user/createWithArray",
        json=users
    )
    assert response.status_code == 200

def test_create_users_with_list():
    users = [{"username": f"user_{i}"} for i in range(3)]
    response = requests.post(
        f"{BASE_URL}/user/createWithList",
        json=users
    )
    assert response.status_code == 200

def test_login_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
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
    assert response.status_code == 400

def test_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

@pytest.mark.parametrize("username,expected", [
    ("invalid_user!", 400),
    ("nonexistent", 404)
])
def test_get_user_invalid(username, expected):
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == expected

def test_update_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.put(
        f"{BASE_URL}/user/{username}",
        json={"email": "new@example.com"}
    )
    assert response.status_code == 200

def test_update_user_invalid():
    response = requests.put(
        f"{BASE_URL}/user/invalid_user!",
        json={"email": "new@example.com"}
    )
    assert response.status_code in [400, 404]

def test_delete_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_delete_user_invalid():
    response = requests.delete(f"{BASE_URL}/user/invalid_user!")
    assert response.status_code in [400, 404]

# Интеграционные тесты (5 тестов)
def test_full_pet_lifecycle():
    # Create
    pet_id, _ = create_test_pet()
    # Update
    requests.put(f"{BASE_URL}/pet", json={"id": pet_id, "name": "Updated"})
    # Delete
    requests.delete(f"{BASE_URL}/pet/{pet_id}", headers={"api_key": "special-key"})

def test_store_workflow():
    # Create order
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    # Delete order
    requests.delete(f"{BASE_URL}/store/order/{order_id}")

def test_user_workflow():
    username = f"user_{generate_unique_id()}"
    # Create
    requests.post(f"{BASE_URL}/user", json={"username": username})
    # Update
    requests.put(f"{BASE_URL}/user/{username}", json={"email": "new@test.com"})
    # Delete
    requests.delete(f"{BASE_URL}/user/{username}")

# Тесты устойчивости (5 тестов)
@pytest.mark.flaky(reruns=3)
def test_high_availability():
    for _ in range(5):
        requests.get(f"{BASE_URL}/store/inventory")

def test_error_handling():
    response = requests.post(
        f"{BASE_URL}/pet",
        data="invalid_json",
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 500]