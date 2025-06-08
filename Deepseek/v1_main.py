import pytest
import requests
import json
import random
import time

BASE_URL = 'https://petstore.swagger.io/v2'

# Helper function to generate unique IDs
def generate_unique_id():
    return random.randint(1, 10**6)

# Unit Tests

# Pet endpoints
def test_post_pet_valid():
    pet_data = {
        "id": generate_unique_id(),
        "name": "ValidPet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/pet', data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 200
    assert response.json()['id'] == pet_data['id']

def test_post_pet_invalid():
    pet_data = {"name": "InvalidPet"}  # Missing photoUrls
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/pet', data=json.dumps(pet_data), headers=headers)
    assert response.status_code == 405

def test_put_pet_valid():
    pet_id = generate_unique_id()
    create_data = {
        "id": pet_id,
        "name": "Initial",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(f'{BASE_URL}/pet', data=json.dumps(create_data), headers=headers)
    update_data = {**create_data, "name": "Updated"}
    response = requests.put(f'{BASE_URL}/pet', data=json.dumps(update_data), headers=headers)
    assert response.status_code == 200

def test_put_pet_invalid():
    update_data = {"id": "invalid", "name": "Invalid"}
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f'{BASE_URL}/pet', data=json.dumps(update_data), headers=headers)
    assert response.status_code == 400

def test_get_pet_by_id_valid():
    pet_id = generate_unique_id()
    create_data = {
        "id": pet_id,
        "name": "TestGet",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(f'{BASE_URL}/pet', data=json.dumps(create_data), headers=headers)
    response = requests.get(f'{BASE_URL}/pet/{pet_id}')
    assert response.status_code == 200

def test_get_pet_by_id_invalid():
    response = requests.get(f'{BASE_URL}/pet/invalid_id')
    assert response.status_code == 400

def test_get_pet_by_id_not_found():
    response = requests.get(f'{BASE_URL}/pet/{generate_unique_id()}')
    assert response.status_code == 404

def test_delete_pet_valid():
    pet_id = generate_unique_id()
    create_data = {
        "id": pet_id,
        "name": "ToDelete",
        "photoUrls": ["http://example.com/photo.jpg"]
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(f'{BASE_URL}/pet', data=json.dumps(create_data), headers=headers)
    headers_delete = {'api_key': 'special-key'}
    response = requests.delete(f'{BASE_URL}/pet/{pet_id}', headers=headers_delete)
    assert response.status_code == 200

def test_delete_pet_invalid():
    headers = {'api_key': 'special-key'}
    response = requests.delete(f'{BASE_URL}/pet/invalid_id', headers=headers)
    assert response.status_code == 400

def test_delete_pet_not_found():
    headers = {'api_key': 'special-key'}
    response = requests.delete(f'{BASE_URL}/pet/{generate_unique_id()}', headers=headers)
    assert response.status_code == 404

def test_get_pet_find_by_status_valid():
    response = requests.get(f'{BASE_URL}/pet/findByStatus', params={'status': 'available'})
    assert response.status_code == 200

def test_get_pet_find_by_status_invalid():
    response = requests.get(f'{BASE_URL}/pet/findByStatus', params={'status': 'invalid'})
    assert response.status_code == 400

# Store endpoints
def test_post_store_order_valid():
    order_data = {
        "id": generate_unique_id(),
        "petId": 123,
        "quantity": 1,
        "shipDate": "2023-10-01T12:00:00Z",
        "status": "placed",
        "complete": False
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/store/order', data=json.dumps(order_data), headers=headers)
    assert response.status_code == 200

def test_post_store_order_invalid():
    order_data = {"petId": "invalid"}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/store/order', data=json.dumps(order_data), headers=headers)
    assert response.status_code == 400

def test_get_store_order_valid():
    order_id = generate_unique_id()
    order_data = {
        "id": order_id,
        "petId": 123,
        "quantity": 1
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(f'{BASE_URL}/store/order', data=json.dumps(order_data), headers=headers)
    response = requests.get(f'{BASE_URL}/store/order/{order_id}')
    assert response.status_code == 200

def test_get_store_order_invalid():
    response = requests.get(f'{BASE_URL}/store/order/invalid_id')
    assert response.status_code == 400

def test_get_store_order_not_found():
    response = requests.get(f'{BASE_URL}/store/order/{generate_unique_id()}')
    assert response.status_code == 404

# User endpoints
def test_post_user_valid():
    user_data = {
        "username": f"user_{generate_unique_id()}",
        "email": "test@example.com"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/user', data=json.dumps(user_data), headers=headers)
    assert response.status_code == 200

def test_post_user_invalid():
    user_data = {"email": "invalid"}  # Missing username
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/user', data=json.dumps(user_data), headers=headers)
    assert response.status_code == 400

def test_get_user_valid():
    username = f"user_{generate_unique_id()}"
    user_data = {"username": username}
    headers = {'Content-Type': 'application/json'}
    requests.post(f'{BASE_URL}/user', data=json.dumps(user_data), headers=headers)
    response = requests.get(f'{BASE_URL}/user/{username}')
    assert response.status_code == 200

def test_get_user_not_found():
    response = requests.get(f'{BASE_URL}/user/invalid_user')
    assert response.status_code == 404

def test_login_user_valid():
    response = requests.get(f'{BASE_URL}/user/login', params={'username': 'test', 'password': 'test'})
    assert response.status_code == 200

def test_login_user_invalid():
    response = requests.get(f'{BASE_URL}/user/login', params={'username': 'invalid', 'password': 'invalid'})
    assert response.status_code == 400

# Integration Tests
def test_crud_pet_flow():
    pet_id = generate_unique_id()
    # Create
    create_data = {
        "id": pet_id,
        "name": "CRUD",
        "photoUrls": ["http://example.com/photo.jpg"]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/pet', data=json.dumps(create_data), headers=headers)
    assert response.status_code == 200
    # Read
    response = requests.get(f'{BASE_URL}/pet/{pet_id}')
    assert response.status_code == 200
    # Update
    update_data = {**create_data, "name": "UPDATED"}
    response = requests.put(f'{BASE_URL}/pet', data=json.dumps(update_data), headers=headers)
    assert response.status_code == 200
    # Delete
    headers_delete = {'api_key': 'special-key'}
    response = requests.delete(f'{BASE_URL}/pet/{pet_id}', headers=headers_delete)
    assert response.status_code == 200

def test_auth_and_access_flow():
    # Assume login is required; this is a simplified example
    session = requests.Session()
    response = session.get(f'{BASE_URL}/user/login', params={'username': 'test', 'password': 'test'})
    assert response.status_code == 200
    # Access protected endpoint
    headers = {'api_key': 'special-key'}
    response = session.delete(f'{BASE_URL}/pet/999', headers=headers)
    assert response.status_code in [200, 404]
    # Test invalid token
    response = requests.delete(f'{BASE_URL}/pet/999', headers={'api_key': 'invalid'})
    assert response.status_code == 401

# Resilience Tests
def test_rate_limit():
    for _ in range(5):
        response = requests.get(f'{BASE_URL}/store/inventory')
    assert response.status_code == 429

def test_large_json_body():
    large_data = {"data": "x" * 10**6}  # 1MB data
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/pet', data=json.dumps(large_data), headers=headers)
    assert response.status_code == 413

def test_timeout():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f'{BASE_URL}/pet/1', timeout=0.001)