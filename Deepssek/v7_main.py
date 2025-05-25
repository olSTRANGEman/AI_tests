import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

#region Helper Functions
def generate_unique_id():
    return random.randint(1, 10**8)

def wait_for_consistency():
    time.sleep(0.3)
#endregion

#region Pet Endpoints (30 тестов)
def test_create_pet_valid():
    pet_id = generate_unique_id()
    data = {
        "id": pet_id,
        "name": "ValidPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200

def test_create_pet_missing_photo():
    data = {"name": "NoPhotoPet"}
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code in [400, 405]

def test_create_pet_invalid_id_type():
    data = {"id": "invalid_id", "name": "InvalidPet"}
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 400

def test_update_pet_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id, "name": "Initial"})
    response = requests.put(f"{BASE_URL}/pet", json={
        "id": pet_id,
        "name": "Updated",
        "photoUrls": ["http://new.url"]
    })
    assert response.status_code == 200

def test_update_pet_invalid_id():
    response = requests.put(f"{BASE_URL}/pet", json={"id": "invalid"})
    assert response.status_code in [400, 404]

def test_update_pet_nonexistent():
    response = requests.put(f"{BASE_URL}/pet", json={"id": 999999999})
    assert response.status_code == 404

def test_find_pets_by_status_available():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert response.status_code == 200

def test_find_pets_by_status_pending():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "pending"})
    assert response.status_code == 200

def test_find_pets_by_status_sold():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "sold"})
    assert response.status_code == 200

def test_find_pets_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid"})
    assert response.status_code == 400

def test_find_pets_by_tags_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={
        "id": pet_id,
        "tags": [{"id": 1, "name": "test_tag"}]
    })
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "test_tag"})
    assert response.status_code == 200

def test_find_pets_by_tags_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "nonexistent_tag"})
    assert response.status_code == 200  # API возвращает пустой список

def test_get_pet_by_id_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    wait_for_consistency()
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

def test_get_pet_by_id_string():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400

def test_get_pet_by_id_negative():
    response = requests.get(f"{BASE_URL}/pet/-1")
    assert response.status_code == 400

def test_get_pet_by_id_nonexistent():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

def test_update_pet_form_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    response = requests.post(
        f"{BASE_URL}/pet/{pet_id}",
        data={"name": "NewName", "status": "pending"}
    )
    assert response.status_code == 200

def test_update_pet_form_invalid_id():
    response = requests.post(
        f"{BASE_URL}/pet/invalid_id",
        data={"status": "invalid"}
    )
    assert response.status_code in [400, 405]

def test_upload_pet_image_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    files = {'file': ('test.jpg', b'content', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files)
    assert response.status_code == 200

def test_upload_pet_image_invalid_id():
    files = {'file': ('test.jpg', b'content')}
    response = requests.post(f"{BASE_URL}/pet/invalid_id/uploadImage", files=files)
    assert response.status_code in [400, 404]

def test_delete_pet_valid():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    response = requests.delete(
        f"{BASE_URL}/pet/{pet_id}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 200

def test_delete_pet_unauthorized():
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code in [401, 403]

def test_delete_pet_invalid_id():
    response = requests.delete(
        f"{BASE_URL}/pet/invalid_id",
        headers={"api_key": "special-key"}
    )
    assert response.status_code in [400, 404]

def test_delete_pet_nonexistent():
    response = requests.delete(
        f"{BASE_URL}/pet/999999999",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 404
#endregion

#region Store Endpoints (15 тестов)
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_create_order_valid():
    order_id = generate_unique_id()
    response = requests.post(f"{BASE_URL}/store/order", json={
        "id": order_id,
        "petId": generate_unique_id(),
        "quantity": 1
    })
    assert response.status_code == 200

def test_create_order_invalid_pet_id():
    response = requests.post(f"{BASE_URL}/store/order", json={
        "id": generate_unique_id(),
        "petId": "invalid",
        "quantity": 1
    })
    assert response.status_code == 400

def test_create_order_missing_fields():
    response = requests.post(f"{BASE_URL}/store/order", json={})
    assert response.status_code == 400

def test_get_order_valid():
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_get_order_string_id():
    response = requests.get(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code == 400

def test_get_order_nonexistent():
    response = requests.get(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_delete_order_valid():
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_order_invalid_id():
    response = requests.delete(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code == 400

def test_delete_order_nonexistent():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404
#endregion

#region User Endpoints (20 тестов)
def test_create_user_valid():
    username = f"user_{generate_unique_id()}"
    response = requests.post(f"{BASE_URL}/user", json={
        "username": username,
        "email": "test@example.com"
    })
    assert response.status_code == 200

def test_create_user_missing_username():
    response = requests.post(f"{BASE_URL}/user", json={"email": "test@example.com"})
    assert response.status_code == 400

def test_create_user_invalid_email():
    response = requests.post(f"{BASE_URL}/user", json={
        "username": "test_user",
        "email": "invalid_email"
    })
    assert response.status_code == 400

def test_create_users_with_array():
    users = [{"username": f"user_{i}"} for i in range(3)]
    response = requests.post(f"{BASE_URL}/user/createWithArray", json=users)
    assert response.status_code == 200

def test_create_users_with_list():
    users = [{"username": f"user_{i}"} for i in range(3)]
    response = requests.post(f"{BASE_URL}/user/createWithList", json=users)
    assert response.status_code == 200

def test_login_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.get(
        f"{BASE_URL}/user/login",
        params={"username": username, "password": "any"}
    )
    assert response.status_code == 200

def test_login_invalid_credentials():
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

def test_get_user_special_chars():
    response = requests.get(f"{BASE_URL}/user/invalid_user!")
    assert response.status_code == 400

def test_get_user_nonexistent():
    response = requests.get(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404

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

def test_delete_user_nonexistent():
    response = requests.delete(f"{BASE_URL}/user/nonexistent_user")
    assert response.status_code == 404
#endregion

#region Интеграционные тесты (5 тестов)
def test_full_pet_lifecycle():
    pet_id = generate_unique_id()
    
    # Create
    create_res = requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    assert create_res.status_code == 200
    
    # Update
    update_res = requests.put(f"{BASE_URL}/pet", json={"id": pet_id, "name": "Updated"})
    assert update_res.status_code == 200
    
    # Delete
    delete_res = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers={"api_key": "special-key"})
    assert delete_res.status_code == 200

def test_store_order_workflow():
    order_id = generate_unique_id()
    
    # Create
    create_res = requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    assert create_res.status_code == 200
    
    # Delete
    delete_res = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert delete_res.status_code == 200

def test_user_workflow():
    username = f"user_{generate_unique_id()}"
    
    # Create
    create_res = requests.post(f"{BASE_URL}/user", json={"username": username})
    assert create_res.status_code == 200
    
    # Update
    update_res = requests.put(f"{BASE_URL}/user/{username}", json={"email": "new@test.com"})
    assert update_res.status_code == 200
    
    # Delete
    delete_res = requests.delete(f"{BASE_URL}/user/{username}")
    assert delete_res.status_code == 200

def test_auth_workflow():
    # Create user
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    
    # Login
    login_res = requests.get(f"{BASE_URL}/user/login", params={"username": username})
    assert login_res.status_code == 200
    
    # Logout
    logout_res = requests.get(f"{BASE_URL}/user/logout")
    assert logout_res.status_code == 200

def test_cross_service_workflow():
    # Create pet
    pet_id = generate_unique_id()
    requests.post(f"{BASE_URL}/pet", json={"id": pet_id})
    
    # Create order
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={
        "id": order_id,
        "petId": pet_id
    })
    
    # Create user
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    
    # Cleanup
    requests.delete(f"{BASE_URL}/pet/{pet_id}")
    requests.delete(f"{BASE_URL}/store/order/{order_id}")
    requests.delete(f"{BASE_URL}/user/{username}")
#endregion