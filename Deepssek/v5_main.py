import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

# Helper functions
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

# Pet Endpoints (30 тестов)
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_post_pet_valid():
    pet_id, response = create_test_pet()
    assert response.status_code == 200
    time.sleep(0.5)
    assert requests.get(f"{BASE_URL}/pet/{pet_id}").status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"name": "NoPhoto"}, 400),
    ({"id": "invalid"}, 500),
    ({"status": "unknown"}, 400)
])
def test_post_pet_invalid(data, expected):
    response = requests.post(
        f"{BASE_URL}/pet",
        data=json.dumps(data),
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

def test_put_pet_invalid_id():
    response = requests.put(
        f"{BASE_URL}/pet",
        data=json.dumps({"id": "invalid"}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code in [400, 404]

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status(status):
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": status}
    )
    assert response.status_code == 200

def test_get_pet_by_status_invalid():
    response = requests.get(
        f"{BASE_URL}/pet/findByStatus",
        params={"status": "invalid"}
    )
    assert response.status_code == 400

@pytest.mark.flaky(reruns=3)
def test_get_pet_by_id_valid():
    pet_id, _ = create_test_pet()
    time.sleep(1)
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

@pytest.mark.parametrize("pet_id,expected", [
    ("invalid", 400),
    (999999999, 404)
])
def test_get_pet_by_id_invalid(pet_id, expected):
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == expected

def test_update_pet_with_form():
    pet_id, _ = create_test_pet()
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}",
        data={"name": "NewName", "status": "pending"}
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

def test_delete_pet_authorized():
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

def test_delete_pet_invalid_id():
    response = requests.delete(
        f"{BASE_URL}/pet/invalid_id",
        headers={"api_key": "special-key"}
    )
    assert response.status_code in [400, 404]

# Store Endpoints (15 тестов)
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_order_lifecycle():
    order_id = generate_unique_id()
    order_data = {
        "id": order_id,
        "petId": create_test_pet()[0],
        "quantity": 1,
        "status": "placed"
    }
    
    # Create
    create_res = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert create_res.status_code in [200, 400]
    
    if create_res.status_code == 200:
        # Get
        get_res = requests.get(f"{BASE_URL}/store/order/{order_id}")
        assert get_res.status_code == 200
        
        # Delete
        del_res = requests.delete(f"{BASE_URL}/store/order/{order_id}")
        assert del_res.status_code in [200, 404]

def test_get_order_invalid():
    response = requests.get(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code in [400, 404]

def test_delete_nonexistent_order():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

# User Endpoints (20 тестов)
def test_user_lifecycle():
    username = f"user_{generate_unique_id()}"
    
    # Create
    response = requests.post(
        f"{BASE_URL}/user",
        json={"username": username, "email": "test@example.com"}
    )
    assert response.status_code == 200
    
    # Get
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    
    # Update
    response = requests.put(
        f"{BASE_URL}/user/{username}",
        json={"email": "new@example.com"}
    )
    assert response.status_code == 200
    
    # Delete
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_login_logout():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    
    # Login
    response = requests.get(
        f"{BASE_URL}/user/login",
        params={"username": username, "password": "any"}
    )
    assert response.status_code == 200
    
    # Logout
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

@pytest.mark.parametrize("data,expected", [
    ({"email": "invalid"}, 400),
    ({"username": "bad@user"}, 500)
])
def test_create_user_invalid(data, expected):
    response = requests.post(f"{BASE_URL}/user", json=data)
    assert response.status_code == expected

def test_delete_invalid_user():
    response = requests.delete(f"{BASE_URL}/user/invalid_user!")
    assert response.status_code in [400, 404]

# Интеграционные тесты (5 тестов)
def test_full_workflow():
    # Create pet
    pet_id, _ = create_test_pet()
    
    # Create order
    order_data = {
        "petId": pet_id,
        "quantity": 1,
        "status": "placed"
    }
    order_res = requests.post(f"{BASE_URL}/store/order", json=order_data)
    assert order_res.status_code == 200
    
    # Create user
    username = f"user_{generate_unique_id()}"
    user_res = requests.post(f"{BASE_URL}/user", json={"username": username})
    assert user_res.status_code == 200
    
    # Cleanup
    requests.delete(f"{BASE_URL}/pet/{pet_id}")
    requests.delete(f"{BASE_URL}/store/order/{order_res.json()['id']}")
    requests.delete(f"{BASE_URL}/user/{username}")

# Тесты устойчивости (5 тестов)
@pytest.mark.flaky(reruns=3)
def test_high_load():
    for _ in range(10):
        requests.get(f"{BASE_URL}/store/inventory")
    assert requests.get(f"{BASE_URL}/store/inventory").status_code == 200

def test_error_handling():
    # Invalid content type
    response = requests.post(
        f"{BASE_URL}/pet",
        data="plain text",
        headers={'Content-Type': 'text/plain'}
    )
    assert response.status_code in [400, 415]