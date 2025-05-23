import pytest
import requests
import json
from requests.exceptions import Timeout

BASE_URL = "https://petstore.swagger.io/v2"
TIMEOUT = 0.001  # for timeout tests

# Helper to generate unique names

def unique_name(prefix="user"):
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# ----------------------
# Endpoint: /pet
# ----------------------

def test_post_pet_valid():
    data = {
        "id": 123456,
        "name": "TestPet",
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/pet", data=json.dumps(data), headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("id") == 123456
    assert isinstance(body.get("name"), str)
    assert body.get("status") in ["available", "pending", "sold"]


def test_post_pet_invalid_missing_name():
    data = {"id": 789}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/pet", data=json.dumps(data), headers=headers)
    assert resp.status_code == 400


def test_get_pet_by_id_valid():
    # ensure pet exists
    data = {"id": 111, "name": "P1", "photoUrls": ["url"], "status": "available"}
    requests.post(f"{BASE_URL}/pet", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/pet/111")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 111


def test_get_pet_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/pet/0")
    assert resp.status_code == 404


def test_put_pet_valid():
    # ensure existing
    data = {"id": 222, "name": "P2", "photoUrls": ["url"], "status": "available"}
    requests.post(f"{BASE_URL}/pet", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    update = {"id": 222, "name": "P2-upd", "status": "sold", "photoUrls": ["url"]}
    resp = requests.put(f"{BASE_URL}/pet", data=json.dumps(update), headers={'Content-Type': 'application/json'})
    assert resp.status_code == 200
    assert resp.json()["name"] == "P2-upd"


def test_put_pet_invalid():
    update = {"name": "NoID"}
    resp = requests.put(f"{BASE_URL}/pet", data=json.dumps(update), headers={'Content-Type': 'application/json'})
    assert resp.status_code == 400


def test_delete_pet_by_id_valid():
    requests.post(f"{BASE_URL}/pet", data=json.dumps({"id":333,"name":"P3","photoUrls":["url"],"status":"available"}), headers={'Content-Type': 'application/json'})
    resp = requests.delete(f"{BASE_URL}/pet/333")
    assert resp.status_code == 200


def test_delete_pet_by_id_not_found():
    resp = requests.delete(f"{BASE_URL}/pet/999999")
    assert resp.status_code == 404


def test_find_pets_by_status_multiple():
    # create two
    for pet_id in (444, 445):
        requests.post(f"{BASE_URL}/pet", data=json.dumps({"id": pet_id, "name": f"P{pet_id}", "photoUrls": ["url"], "status": "pending"}), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/pet/findByStatus?status=pending")
    assert resp.status_code == 200
    arr = resp.json()
    assert isinstance(arr, list)
    assert any(p.get("id") == 444 for p in arr)


def test_find_pets_by_status_any():
    resp = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid")
    # spec defines only 200 for findByStatus
    assert resp.status_code == 200


def test_find_pets_by_tags_single():
    requests.post(f"{BASE_URL}/pet", data=json.dumps({"id":555,"name":"P6","photoUrls":["url"],"status":"available","tags":[{"id":10,"name":"sale"}]}), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/pet/findByTags?tags=sale")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_find_pets_by_tags_any():
    resp = requests.get(f"{BASE_URL}/pet/findByTags?tags=")
    # spec defines only 200
    assert resp.status_code == 200

# ----------------------
# Endpoint: /pet/{petId}/uploadImage
# ----------------------

def test_upload_image_valid(tmp_path):
    file = tmp_path / "img.jpg"
    file.write_bytes(b"\xff\xd8\xff")
    resp = requests.post(f"{BASE_URL}/pet/111/uploadImage", files={"file": open(file, 'rb')})
    assert resp.status_code == 200


def test_upload_image_invalid_no_file():
    resp = requests.post(f"{BASE_URL}/pet/111/uploadImage")
    assert resp.status_code != 200

# ----------------------
# Endpoint: /store/inventory
# ----------------------

def test_get_inventory():
    resp = requests.get(f"{BASE_URL}/store/inventory")
    assert resp.status_code == 200
    inv = resp.json()
    assert "sold" in inv and isinstance(inv.get("sold"), int)

# ----------------------
# Endpoint: /store/order
# ----------------------

def test_place_order_valid():
    data = {"id":1,"petId":111,"quantity":2,"shipDate":"2025-05-22T00:00:00.000Z","status":"placed","complete":True}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/store/order", data=json.dumps(data), headers=headers)
    assert resp.status_code == 200


def test_place_order_invalid():
    data = {"petId":"x"}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/store/order", data=json.dumps(data), headers=headers)
    assert resp.status_code == 400


def test_get_order_by_id_valid():
    data = {"id":2,"petId":111,"quantity":1,"shipDate":"2025-05-22T00:00:00.000Z","status":"placed","complete":False}
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/store/order/2")
    assert resp.status_code == 200
    assert resp.json().get("id") == 2


def test_get_order_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/store/order/0")
    assert resp.status_code == 404


def test_delete_order_by_id_valid():
    data = {"id":3,"petId":111,"quantity":1,"shipDate":"2025-05-22T00:00:00.000Z","status":"placed","complete":False}
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    resp = requests.delete(f"{BASE_URL}/store/order/3")
    assert resp.status_code == 200


def test_delete_order_by_id_not_found():
    resp = requests.delete(f"{BASE_URL}/store/order/9999")
    assert resp.status_code == 404

# ----------------------
# Endpoint: /user
# ----------------------

def test_create_user_valid():
    username = unique_name("u")
    data = {"id":10,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/user", data=json.dumps(data), headers=headers)
    assert resp.status_code == 200


def test_create_user_invalid_missing_required():
    data = {"id":11}
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/user", data=json.dumps(data), headers=headers)
    assert resp.status_code == 400


def test_create_users_with_array_valid():
    users = [{"id":12,"username":"u1","firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}]
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/user/createWithArray", data=json.dumps(users), headers=headers)
    assert resp.status_code == 200


def test_create_users_with_list_valid():
    users = [{"id":13,"username":"u2","firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}]
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE_URL}/user/createWithList", data=json.dumps(users), headers=headers)
    assert resp.status_code == 200

# ----------------------
# Endpoint: /user/login & /user/logout
# ----------------------

def test_login_valid():
    username = unique_name("u")
    password = "pass"
    requests.post(f"{BASE_URL}/user", data=json.dumps({"id":14,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":password,"phone":"123","userStatus":1}), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/user/login?username={username}&password={password}")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_login_invalid():
    resp = requests.get(f"{BASE_URL}/user/login?username=nope&password=wrong")
    assert resp.status_code == 400


def test_logout():
    resp = requests.get(f"{BASE_URL}/user/logout")
    assert resp.status_code == 200

# ----------------------
# Endpoint: /user/{username}
# ----------------------

def test_get_user_by_username_valid():
    username = unique_name("u")
    data = {"id":15,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}
    requests.post(f"{BASE_URL}/user", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    resp = requests.get(f"{BASE_URL}/user/{username}")
    assert resp.status_code == 200
    assert resp.json().get("username") == username


def test_get_user_by_username_not_found():
    resp = requests.get(f"{BASE_URL}/user/noexist")
    assert resp.status_code == 404


def test_update_user_valid():
    username = unique_name("u")
    data = {"id":16,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}
    requests.post(f"{BASE_URL}/user", data=json.dumps(data), headers={'Content-Type': 'application/json'})
    update = {"firstName":"F2","lastName":"L2","email":"b@c.com","password":"pass2","phone":"456","userStatus":2}
    resp = requests.put(f"{BASE_URL}/user/{username}", data=json.dumps(update), headers={'Content-Type': 'application/json'})
    assert resp.status_code == 200


def test_update_user_not_found():
    resp = requests.put(f"{BASE_URL}/user/noexist", data=json.dumps({"firstName":"X"}), headers={'Content-Type': 'application/json'})
    assert resp.status_code == 404


def test_delete_user_valid():
    username = unique_name("u")
    requests.post(f"{BASE_URL}/user", data=json.dumps({"id":17,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":"pass","phone":"123","userStatus":1}), headers={'Content-Type': 'application/json'})
    resp = requests.delete(f"{BASE_URL}/user/{username}")
    assert resp.status_code == 200


def test_delete_user_not_found():
    resp = requests.delete(f"{BASE_URL}/user/noexist")
    assert resp.status_code == 404

# ----------------------
# Integration flows
# ----------------------

def test_crud_pet_flow():
    headers = {'Content-Type': 'application/json'}
    # Create
    data = {"id":200,"name":"FlowPet","photoUrls":["url"],"status":"available"}
    r = requests.post(f"{BASE_URL}/pet", data=json.dumps(data), headers=headers)
    assert r.status_code == 200
    # Read
    r = requests.get(f"{BASE_URL}/pet/200")
    assert r.status_code == 200
    # Update
    r = requests.put(f"{BASE_URL}/pet", data=json.dumps({"id":200,"name":"FlowPet2","status":"sold","photoUrls":["url"]}), headers=headers)
    assert r.status_code == 200
    # Delete
    r = requests.delete(f"{BASE_URL}/pet/200")
    assert r.status_code == 200


def test_auth_and_access_flow():
    username = unique_name("u")
    password = "pass"
    # setup user
    requests.post(f"{BASE_URL}/user", data=json.dumps({"id":300,"username":username,"firstName":"F","lastName":"L","email":"a@b.com","password":password,"phone":"123","userStatus":1}), headers={'Content-Type': 'application/json'})
    r = requests.get(f"{BASE_URL}/user/login?username={username}&password={password}")
    assert r.status_code == 200
    msg = r.json().get("message")
    token = msg.split(":")[-1] if msg else None
    # protected access
    r2 = requests.get(f"{BASE_URL}/store/inventory", headers={"Authorization": f"Bearer wrongtoken"})
    assert r2.status_code in (401,403)

# ----------------------
# Resilience & Load tests
# ----------------------

def test_rate_limit_pet():
    last = None
    for _ in range(10):
        last = requests.get(f"{BASE_URL}/pet/111")
    assert last.status_code in (200,429)


def test_large_payload_pet():
    big = {"id":999,"name":"x","photoUrls":["url"],"status":"available","tags":[{"id":i,"name":"n"} for i in range(10000)]}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(f"{BASE_URL}/pet", data=json.dumps(big), headers=headers)
    assert r.status_code in (413,200)


def test_timeout_pet_get():
    with pytest.raises(Timeout):
        requests.get(f"{BASE_URL}/pet/111", timeout=TIMEOUT)
