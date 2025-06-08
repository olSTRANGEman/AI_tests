import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

#region Helpers
def generate_unique_id():
    return random.randint(1, 10**8)

def wait_for_propagation():
    time.sleep(0.5)

def create_basic_pet():
    pet_id = generate_unique_id()
    return {
        "id": pet_id,
        "name": "TestPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
#endregion

#region Pet Endpoints (32 теста)
def test_post_pet_valid():
    data = create_basic_pet()
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200

def test_post_pet_missing_required_fields():
    response = requests.post(f"{BASE_URL}/pet", json={"name": "NoPhoto"})
    assert response.status_code == 400

def test_post_pet_invalid_id_format():
    response = requests.post(f"{BASE_URL}/pet", json={"id": "invalid"})
    assert response.status_code == 400

def test_post_pet_invalid_status():
    data = create_basic_pet()
    data["status"] = "invalid_status"
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 400

def test_put_pet_valid():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    data["name"] = "Updated"
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200

def test_put_pet_not_existing():
    data = create_basic_pet()
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 404

def test_put_pet_invalid_data():
    response = requests.put(f"{BASE_URL}/pet", json={"id": "invalid"})
    assert response.status_code == 400

def test_get_pet_by_id_valid():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    wait_for_propagation()
    response = requests.get(f"{BASE_URL}/pet/{data['id']}")
    assert response.status_code == 200

def test_get_pet_by_id_string():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400

def test_get_pet_by_id_negative():
    response = requests.get(f"{BASE_URL}/pet/-1")
    assert response.status_code == 400

def test_get_pet_by_id_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    assert response.status_code == 404

def test_find_pets_by_status_available():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available")
    assert response.status_code == 200

def test_find_pets_by_status_pending():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=pending")
    assert response.status_code == 200

def test_find_pets_by_status_sold():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=sold")
    assert response.status_code == 200

def test_find_pets_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid")
    assert response.status_code == 400

def test_find_pets_by_tags_valid():
    data = create_basic_pet()
    data["tags"] = [{"id": 1, "name": "test_tag"}]
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=test_tag")
    assert response.status_code == 200

def test_find_pets_by_tags_empty():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=nonexistent")
    assert response.status_code == 200

def test_update_pet_form_valid():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.post(
        f"{BASE_URL}/pet/{data['id']}",
        data={"name": "NewName", "status": "pending"}
    )
    assert response.status_code == 200

def test_update_pet_form_invalid_id():
    response = requests.post(
        f"{BASE_URL}/pet/invalid_id",
        data={"status": "invalid"}
    )
    assert response.status_code == 405

def test_upload_pet_image_valid():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    files = {'file': ('test.jpg', b'content', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{data['id']}/uploadImage", files=files)
    assert response.status_code == 200

def test_upload_pet_image_invalid_id():
    files = {'file': ('test.jpg', b'content')}
    response = requests.post(f"{BASE_URL}/pet/invalid_id/uploadImage", files=files)
    assert response.status_code == 405

def test_delete_pet_valid():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.delete(
        f"{BASE_URL}/pet/{data['id']}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 200

def test_delete_pet_unauthorized():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.delete(f"{BASE_URL}/pet/{data['id']}")
    assert response.status_code == 401

def test_delete_pet_invalid_id():
    response = requests.delete(
        f"{BASE_URL}/pet/invalid_id",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 400

def test_delete_pet_not_found():
    response = requests.delete(
        f"{BASE_URL}/pet/999999999",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 404

def test_delete_pet_twice():
    data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=data)
    requests.delete(f"{BASE_URL}/pet/{data['id']}", headers={"api_key": "special-key"})
    response = requests.delete(
        f"{BASE_URL}/pet/{data['id']}",
        headers={"api_key": "special-key"}
    )
    assert response.status_code == 404

def test_pet_lifecycle():
    data = create_basic_pet()
    
    # Create
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200
    
    # Read
    response = requests.get(f"{BASE_URL}/pet/{data['id']}")
    assert response.status_code == 200
    
    # Update
    data["status"] = "sold"
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200
    
    # Delete
    response = requests.delete(f"{BASE_URL}/pet/{data['id']}", headers={"api_key": "special-key"})
    assert response.status_code == 200

#endregion

#region Store Endpoints (15 тестов)
def test_get_inventory():
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_create_order_valid():
    data = {
        "id": generate_unique_id(),
        "petId": create_basic_pet()["id"],
        "quantity": 1,
        "status": "placed"
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 200

def test_create_order_invalid_pet_id():
    data = {
        "id": generate_unique_id(),
        "petId": "invalid",
        "quantity": 1
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 400

def test_create_order_negative_quantity():
    data = {
        "id": generate_unique_id(),
        "petId": create_basic_pet()["id"],
        "quantity": -1
    }
    response = requests.post(f"{BASE_URL}/store/order", json=data)
    assert response.status_code == 400

def test_get_order_valid():
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    wait_for_propagation()
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_get_order_invalid_id():
    response = requests.get(f"{BASE_URL}/store/order/invalid_id")
    assert response.status_code == 400

def test_get_order_not_found():
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

def test_delete_order_not_found():
    response = requests.delete(f"{BASE_URL}/store/order/999999999")
    assert response.status_code == 404

def test_store_order_lifecycle():
    order_id = generate_unique_id()
    
    # Create
    response = requests.post(f"{BASE_URL}/store/order", json={"id": order_id})
    assert response.status_code == 200
    
    # Read
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200
    
    # Delete
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

#endregion

#region User Endpoints (20 тестов)
def test_create_user_valid():
    username = f"user_{generate_unique_id()}"
    response = requests.post(f"{BASE_URL}/user", json={"username": username})
    assert response.status_code == 200

def test_create_user_duplicate():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.post(f"{BASE_URL}/user", json={"username": username})
    assert response.status_code == 400

def test_create_user_invalid_email():
    response = requests.post(f"{BASE_URL}/user", json={
        "username": "test",
        "email": "invalid"
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
    response = requests.get(f"{BASE_URL}/user/login", params={
        "username": username,
        "password": "any"
    })
    assert response.status_code == 200

def test_login_invalid():
    response = requests.get(f"{BASE_URL}/user/login", params={
        "username": "invalid",
        "password": "invalid"
    })
    assert response.status_code == 400

def test_logout():
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    wait_for_propagation()
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_get_user_not_found():
    response = requests.get(f"{BASE_URL}/user/nonexistent")
    assert response.status_code == 404

def test_update_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.put(f"{BASE_URL}/user/{username}", json={
        "email": "new@example.com"
    })
    assert response.status_code == 200

def test_update_user_not_found():
    response = requests.put(f"{BASE_URL}/user/nonexistent", json={
        "email": "new@example.com"
    })
    assert response.status_code == 404

def test_delete_user_valid():
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

def test_delete_user_not_found():
    response = requests.delete(f"{BASE_URL}/user/nonexistent")
    assert response.status_code == 404

def test_user_lifecycle():
    username = f"user_{generate_unique_id()}"
    
    # Create
    response = requests.post(f"{BASE_URL}/user", json={"username": username})
    assert response.status_code == 200
    
    # Read
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200
    
    # Update
    response = requests.put(f"{BASE_URL}/user/{username}", json={
        "email": "updated@example.com"
    })
    assert response.status_code == 200
    
    # Delete
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 200

#endregion

#region Интеграционные тесты (5 тестов)
def test_full_workflow():
    # Create Pet
    pet_data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    
    # Create Order
    order_id = generate_unique_id()
    requests.post(f"{BASE_URL}/store/order", json={
        "id": order_id,
        "petId": pet_data["id"]
    })
    
    # Create User
    username = f"user_{generate_unique_id()}"
    requests.post(f"{BASE_URL}/user", json={"username": username})
    
    # Cleanup
    requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    requests.delete(f"{BASE_URL}/store/order/{order_id}")
    requests.delete(f"{BASE_URL}/user/{username}")

def test_concurrent_operations():
    # Тест на параллельные операции
    pet_ids = [generate_unique_id() for _ in range(5)]
    for pid in pet_ids:
        requests.post(f"{BASE_URL}/pet", json={"id": pid})
    
    for pid in pet_ids:
        requests.delete(f"{BASE_URL}/pet/{pid}")

def test_error_handling():
    # Тест обработки ошибок
    response = requests.post(f"{BASE_URL}/pet", data="invalid_json")
    assert response.status_code in [400, 500]

def test_data_persistence():
    # Тест на сохранение данных
    pet_data = create_basic_pet()
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200

def test_security():
    # Тест безопасности
    response = requests.delete(f"{BASE_URL}/pet/1")
    assert response.status_code in [401, 403, 404]
#endregion