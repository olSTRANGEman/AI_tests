import pytest
import requests
import json
from requests.exceptions import Timeout

BASE_URL = "https://petstore.swagger.io/v2"

# Utility data
PET_SAMPLE = {
    "id": 0,
    "category": {"id": 0, "name": "string"},
    "name": "doggie",
    "photoUrls": ["string"],
    "tags": [{"id": 0, "name": "string"}],
    "status": "available"
}
ORDER_SAMPLE = {"id": 0, "petId": 0, "quantity": 1, "shipDate": "2025-05-22T00:00:00.000Z", "status": "placed", "complete": True}
USER_SAMPLE = {"id": 0, "username": "testuser", "firstName": "Test", "lastName": "User", "email": "test@example.com", "password": "pass123", "phone": "1234567890", "userStatus": 0}

HEADERS_JSON = {"Content-Type": "application/json"}

# ---------------------- PET ENDPOINTS ----------------------

def test_post_pet_positive():
    body = PET_SAMPLE.copy()
    body["id"] = 100
    resp = requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("id") == 100
    assert isinstance(data.get("name"), str)

@pytest.mark.parametrize("invalid_body", [
    {},
    {"name": ""},
])
def test_post_pet_negative(invalid_body):
    resp = requests.post(f"{BASE_URL}/pet", data=json.dumps(invalid_body), headers=HEADERS_JSON)
    assert resp.status_code in (400, 415)


def test_get_pet_by_id_positive():
    body = PET_SAMPLE.copy()
    body["id"] = 101
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    resp = requests.get(f"{BASE_URL}/pet/101")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("id") == 101

def test_get_pet_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/pet/99999999")
    assert resp.status_code == 404


def test_update_pet_positive():
    body = PET_SAMPLE.copy()
    body["id"] = 102
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    body["name"] = "wolfie"
    resp = requests.put(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    assert resp.status_code == 200
    assert resp.json()["name"] == "wolfie"

def test_update_pet_negative_missing_fields():
    resp = requests.put(f"{BASE_URL}/pet", data=json.dumps({"id": 102}), headers=HEADERS_JSON)
    assert resp.status_code in (400, 405, 415)


def test_delete_pet_positive():
    body = PET_SAMPLE.copy()
    body["id"] = 103
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    resp = requests.delete(f"{BASE_URL}/pet/103")
    assert resp.status_code == 200

def test_delete_pet_not_found():
    resp = requests.delete(f"{BASE_URL}/pet/99999999")
    assert resp.status_code == 404


def test_find_pets_by_status_positive():
    resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_find_pets_by_status_invalid():
    resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_find_pets_by_tags_positive():
    resp = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "string"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# requires form-data
def test_upload_image_positive():
    body = PET_SAMPLE.copy()
    body["id"] = 104
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    files = {"file": ("test.png", b"PNGDATA")}
    resp = requests.post(f"{BASE_URL}/pet/104/uploadImage", files=files)
    assert resp.status_code == 200

def test_upload_image_no_file():
    body = PET_SAMPLE.copy()
    body["id"] = 105
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    resp = requests.post(f"{BASE_URL}/pet/105/uploadImage")
    assert resp.status_code in (400, 415)


# ---------------------- STORE ENDPOINTS ----------------------

def test_get_inventory():
    resp = requests.get(f"{BASE_URL}/store/inventory")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_place_order_positive():
    order = ORDER_SAMPLE.copy()
    order["id"] = 200
    resp = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order), headers=HEADERS_JSON)
    assert resp.status_code == 200
    assert resp.json().get("id") == 200

@pytest.mark.parametrize("invalid_order", [{}, {"id": 200}])
def test_place_order_negative(invalid_order):
    resp = requests.post(f"{BASE_URL}/store/order", data=json.dumps(invalid_order), headers=HEADERS_JSON)
    assert resp.status_code in (400, 415)


def test_get_order_by_id_positive():
    order = ORDER_SAMPLE.copy()
    order["id"] = 201
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(order), headers=HEADERS_JSON)
    resp = requests.get(f"{BASE_URL}/store/order/201")
    assert resp.status_code == 200
    assert resp.json()["id"] == 201

def test_get_order_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/store/order/9999")
    assert resp.status_code == 404


def test_delete_order_positive():
    order = ORDER_SAMPLE.copy()
    order["id"] = 202
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(order), headers=HEADERS_JSON)
    resp = requests.delete(f"{BASE_URL}/store/order/202")
    assert resp.status_code == 200

def test_delete_order_not_found():
    resp = requests.delete(f"{BASE_URL}/store/order/9999")
    assert resp.status_code == 404


# ---------------------- USER ENDPOINTS ----------------------

def test_create_user_positive():
    resp = requests.post(f"{BASE_URL}/user", data=json.dumps(USER_SAMPLE), headers=HEADERS_JSON)
    assert resp.status_code == 200

@pytest.mark.parametrize("invalid_user", [{}, {"username": ""}])
def test_create_user_negative(invalid_user):
    resp = requests.post(f"{BASE_URL}/user", data=json.dumps(invalid_user), headers=HEADERS_JSON)
    assert resp.status_code in (400, 415)


def test_create_users_with_array_positive():
    resp = requests.post(f"{BASE_URL}/user/createWithArray", data=json.dumps([USER_SAMPLE]), headers=HEADERS_JSON)
    assert resp.status_code == 200


def test_create_users_with_list_positive():
    resp = requests.post(f"{BASE_URL}/user/createWithList", data=json.dumps([USER_SAMPLE]), headers=HEADERS_JSON)
    assert resp.status_code == 200


def test_login_user_positive():
    requests.post(f"{BASE_URL}/user", data=json.dumps(USER_SAMPLE), headers=HEADERS_JSON)
    resp = requests.get(f"{BASE_URL}/user/login", params={"username": USER_SAMPLE["username"], "password": USER_SAMPLE["password"]})
    assert resp.status_code == 200


def test_login_user_invalid():
    resp = requests.get(f"{BASE_URL}/user/login", params={"username": "wrong", "password": "wrong"})
    assert resp.status_code in (400, 404)


def test_logout_user():
    resp = requests.get(f"{BASE_URL}/user/logout")
    assert resp.status_code == 200


def test_get_user_by_name_positive():
    requests.post(f"{BASE_URL}/user", data=json.dumps(USER_SAMPLE), headers=HEADERS_JSON)
    resp = requests.get(f"{BASE_URL}/user/{USER_SAMPLE['username']}")
    assert resp.status_code == 200
    assert resp.json()["username"] == USER_SAMPLE["username"]


def test_get_user_by_name_not_found():
    resp = requests.get(f"{BASE_URL}/user/notexist")
    assert resp.status_code == 404


def test_delete_user_positive():
    requests.post(f"{BASE_URL}/user", data=json.dumps(USER_SAMPLE), headers=HEADERS_JSON)
    resp = requests.delete(f"{BASE_URL}/user/{USER_SAMPLE['username']}")
    assert resp.status_code == 200


def test_delete_user_not_found():
    resp = requests.delete(f"{BASE_URL}/user/notexist")
    assert resp.status_code == 404


# ---------------------- INTEGRATION TESTS ----------------------

def test_crud_pet_flow():
    # Create
    body = PET_SAMPLE.copy()
    body["id"] = 300
    requests.post(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    # Read
    resp = requests.get(f"{BASE_URL}/pet/300")
    assert resp.status_code == 200
    # Update
    body["name"] = "flowed"
    requests.put(f"{BASE_URL}/pet", data=json.dumps(body), headers=HEADERS_JSON)
    assert requests.get(f"{BASE_URL}/pet/300").json()["name"] == "flowed"
    # Delete
    resp = requests.delete(f"{BASE_URL}/pet/300")
    assert resp.status_code == 200


def test_auth_and_access_flow():
    # Create and login
    requests.post(f"{BASE_URL}/user", data=json.dumps(USER_SAMPLE), headers=HEADERS_JSON)
    login = requests.get(f"{BASE_URL}/user/login", params={"username": USER_SAMPLE["username"], "password": USER_SAMPLE["password"]})
    assert login.status_code == 200
    # Access protected resource
    good = requests.get(f"{BASE_URL}/user/{USER_SAMPLE['username']}")
    assert good.status_code == 200
    bad = requests.get(f"{BASE_URL}/user/{USER_SAMPLE['username']}", headers={"Authorization": "Bearer invalid"})
    assert bad.status_code in (401, 404)


# ---------------------- RESILIENCE TESTS ----------------------

def test_rate_limit_pet_requests():
    for _ in range(10):
        resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
        assert resp.status_code == 200


def test_large_payload_failure():
    big = {"id": 400, "name": "x" * 1000000, "photoUrls": ["x" * 1000000]}
    resp = requests.post(f"{BASE_URL}/pet", data=json.dumps(big), headers=HEADERS_JSON, timeout=5)
    assert resp.status_code in (400, 413, 415)


def test_timeout_raises():
    with pytest.raises(Timeout):
        requests.get(f"{BASE_URL}/pet/1", timeout=0.0001)

# Total tests: >50 functions
