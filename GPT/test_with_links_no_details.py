import pytest
import requests
from jsonschema import validate

BASE_URL = "https://petstore.swagger.io/v2"

# Schemas for validation
PET_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "status"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "status": {"type": "string"}
    }
}
USER_SCHEMA = {
    "type": "object",
    "required": ["id", "username", "email"],
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string"}
    }
}
ORDER_SCHEMA = {
    "type": "object",
    "required": ["id", "petId", "quantity", "status"],
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "status": {"type": "string"}
    }
}

@pytest.fixture
def new_pet():
    return {"id": 123456, "name": "test_pet", "status": "available"}

@pytest.fixture
def new_user():
    return {"id": 654321, "username": "test_user", "firstName": "First", "lastName": "Last", "email": "test@example.com", "password": "pass", "phone": "12345", "userStatus": 1}

@pytest.fixture
def new_order(new_pet):
    return {"id": 111, "petId": new_pet["id"], "quantity": 1, "status": "placed", "shipDate": "2025-05-22T00:00:00.000Z", "complete": False}

# ------------------ Pet endpoint tests ------------------

def test_post_pet_positive(new_pet):
    r = requests.post(f"{BASE_URL}/pet", json=new_pet)
    assert r.status_code == 200
    validate(r.json(), PET_SCHEMA)

@pytest.mark.parametrize("invalid_body", [{}, {"name": "no_id"}, {"id": "str", "name": 5}])
def test_post_pet_negative(invalid_body):
    r = requests.post(f"{BASE_URL}/pet", json=invalid_body)
    assert r.status_code >= 400


def test_get_pet_by_id_positive(new_pet):
    requests.post(f"{BASE_URL}/pet", json=new_pet)
    r = requests.get(f"{BASE_URL}/pet/{new_pet['id']}")
    assert r.status_code == 200
    validate(r.json(), PET_SCHEMA)

@pytest.mark.parametrize("bad_id", [-1, 0, 9999999999])
def test_get_pet_by_id_not_found(bad_id):
    r = requests.get(f"{BASE_URL}/pet/{bad_id}")
    assert r.status_code in (404,)


def test_put_pet_positive(new_pet):
    requests.post(f"{BASE_URL}/pet", json=new_pet)
    update = {**new_pet, "name": "updated"}
    r = requests.put(f"{BASE_URL}/pet", json=update)
    assert r.status_code == 200
    assert r.json()["name"] == "updated"


def test_find_pets_by_status():
    r = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_find_pets_by_tags():
    r = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "tag1,tag2"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_delete_pet_positive(new_pet):
    requests.post(f"{BASE_URL}/pet", json=new_pet)
    r = requests.delete(f"{BASE_URL}/pet/{new_pet['id']}")
    assert r.status_code == 200

def test_delete_pet_not_found():
    r = requests.delete(f"{BASE_URL}/pet/999999")
    assert r.status_code >= 400

# ------------------ User endpoint tests ------------------

def test_create_user_positive(new_user):
    r = requests.post(f"{BASE_URL}/user", json=new_user)
    assert r.status_code == 200

@pytest.mark.parametrize("invalid_user", [{}, {"username": "no_id"}])
def test_create_user_negative(invalid_user):
    r = requests.post(f"{BASE_URL}/user", json=invalid_user)
    assert r.status_code >= 400


def test_get_user_by_username_positive(new_user):
    requests.post(f"{BASE_URL}/user", json=new_user)
    r = requests.get(f"{BASE_URL}/user/{new_user['username']}")
    assert r.status_code == 200
    validate(r.json(), USER_SCHEMA)

@pytest.mark.parametrize("name", ["unknown", ""])
def test_get_user_by_username_not_found(name):
    r = requests.get(f"{BASE_URL}/user/{name}")
    assert r.status_code in (404, 405)


def test_login_logout_flow(new_user):
    requests.post(f"{BASE_URL}/user", json=new_user)
    r = requests.get(f"{BASE_URL}/user/login", params={"username": new_user['username'], "password": new_user['password']})
    assert r.status_code == 200
    assert 'message' in r.json()
    r2 = requests.get(f"{BASE_URL}/user/logout")
    assert r2.status_code == 200

# ------------------ Store endpoint tests ------------------

def test_get_inventory():
    r = requests.get(f"{BASE_URL}/store/inventory")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


def test_place_order_positive(new_order):
    r = requests.post(f"{BASE_URL}/store/order", json=new_order)
    assert r.status_code == 200
    validate(r.json(), ORDER_SCHEMA)

@pytest.mark.parametrize("bad_order", [{}, {"id": "str"}])
def test_place_order_negative(bad_order):
    r = requests.post(f"{BASE_URL}/store/order", json=bad_order)
    assert r.status_code >= 400


def test_get_order_by_id_positive(new_order):
    requests.post(f"{BASE_URL}/store/order", json=new_order)
    r = requests.get(f"{BASE_URL}/store/order/{new_order['id']}")
    assert r.status_code == 200
    validate(r.json(), ORDER_SCHEMA)

@pytest.mark.parametrize("oid", [-1, 999999])
def test_get_order_by_id_not_found(oid):
    r = requests.get(f"{BASE_URL}/store/order/{oid}")
    assert r.status_code >= 400


def test_delete_order_positive(new_order):
    requests.post(f"{BASE_URL}/store/order", json=new_order)
    r = requests.delete(f"{BASE_URL}/store/order/{new_order['id']}")
    assert r.status_code == 200

def test_delete_order_not_found():
    r = requests.delete(f"{BASE_URL}/store/order/999999")
    assert r.status_code >= 400

# ------------------ Integration tests ------------------

def test_crud_pet_flow():
    pet = {"id": 222, "name": "flow_pet", "status": "available"}
    r = requests.post(f"{BASE_URL}/pet", json=pet)
    assert r.status_code == 200
    r = requests.get(f"{BASE_URL}/pet/{pet['id']}")
    assert r.status_code == 200
    pet['status'] = 'sold'
    r = requests.put(f"{BASE_URL}/pet", json=pet)
    assert r.status_code == 200
    r = requests.delete(f"{BASE_URL}/pet/{pet['id']}")
    assert r.status_code == 200


def test_auth_and_access_flow(new_user):
    requests.post(f"{BASE_URL}/user", json=new_user)
    r = requests.get(f"{BASE_URL}/user/login", params={"username": new_user['username'], "password": new_user['password']})
    token = r.json().get('message')
    headers = {"api_key": token}
    r2 = requests.get(f"{BASE_URL}/store/inventory", headers=headers)
    assert r2.status_code == 200
    # invalid token should not retrieve inventory data
    r3 = requests.get(f"{BASE_URL}/store/inventory", headers={"api_key": "bad"})
    assert r3.status_code >= 400

# ------------------ Resilience tests ------------------

def test_rate_limit_pet():
    for _ in range(20):
        requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    r = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert r.status_code in (200, 429)


def test_large_payload_timeout(new_pet):
    big = {"id": new_pet['id'], "name": "x" * 1000000, "status": "available"}
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(f"{BASE_URL}/pet", json=big, timeout=0.001)


def test_timeout_exception():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"}, timeout=0.0001)

# Additional tests to total >=50 functions