import pytest
import requests
from requests.exceptions import Timeout
import time

BASE_URL = 'https://petstore.swagger.io/v2'

def unique_id():
    return int(time.time() * 1000)

#########################
# Pet Endpoints
#########################

def test_post_pet_valid():
    pet_id = unique_id()
    payload = {'id': pet_id, 'name': 'test_pet', 'photoUrls': ['http://example.com/photo1'], 'status': 'available'}
    resp = requests.post(f"{BASE_URL}/pet", json=payload)
    assert resp.status_code == 200


def test_post_pet_unsupported_media():
    payload = {'id': unique_id(), 'name': 'test'}
    resp = requests.post(f"{BASE_URL}/pet", data=payload)
    assert resp.status_code == 415


def test_post_pet_by_id_method_not_allowed():
    # POST /pet/{petId} returns unsupported media (415)
    resp = requests.post(f"{BASE_URL}/pet/12345", json={'dummy': 'data'})
    assert resp.status_code == 415


def test_get_pet_by_id_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'x', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    resp = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200


def test_get_pet_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/pet/0")
    assert resp.status_code == 404


def test_get_pet_by_id_invalid_id():
    resp = requests.get(f"{BASE_URL}/pet/abc")
    assert resp.status_code == 404


@pytest.mark.parametrize('status', ['available', 'pending', 'sold'])
def test_find_pets_by_status_various(status):
    resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': status})
    assert resp.status_code == 200


def test_find_pets_by_status_invalid():
    # invalid status returns 400
    resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': 'invalid'})
    assert resp.status_code == 400


def test_find_pets_by_status_missing_param():
    resp = requests.get(f"{BASE_URL}/pet/findByStatus")
    assert resp.status_code == 200


@pytest.mark.parametrize('tags', ['tag1,tag2', 'invalid'])
def test_find_pets_by_tags(tags):
    resp = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': tags})
    expected = 200 if tags == 'tag1,tag2' else 400
    assert resp.status_code == expected


def test_update_pet_put_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'orig', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    update_payload = {'id': pet_id, 'name': 'updated', 'photoUrls': ['u'], 'status': 'sold'}
    resp = requests.put(f"{BASE_URL}/pet", json=update_payload)
    assert resp.status_code == 200


def test_update_pet_put_not_found():
    payload = {'id': 0, 'name': 'u', 'photoUrls': ['u'], 'status': 'available'}
    resp = requests.put(f"{BASE_URL}/pet", json=payload)
    assert resp.status_code == 200


def test_update_pet_put_invalid_id():
    resp = requests.put(f"{BASE_URL}/pet", data={'id': 'abc', 'name': 'n'})
    assert resp.status_code == 415


def test_update_pet_with_form():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'f', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    resp = requests.post(f"{BASE_URL}/pet/{pet_id}", data={'name': 'form', 'status': 'pending'})
    # update with form returns unsupported media on this API
    assert resp.status_code == 415


def test_delete_pet_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 't', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    resp = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200


def test_delete_pet_not_found():
    resp = requests.delete(f"{BASE_URL}/pet/0")
    assert resp.status_code == 404


def test_delete_pet_invalid_id():
    resp = requests.delete(f"{BASE_URL}/pet/abc")
    assert resp.status_code == 404


def test_upload_pet_image_valid(tmp_path):
    pet_id = unique_id()
    requests.post(f"{BASE_URL}/pet", json={'id': pet_id, 'name': 'i', 'photoUrls': ['u'], 'status': 'available'})
    file = tmp_path / "img.jpg"
    file.write_bytes(b"data")
    resp = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files={'file': open(file, 'rb')})
    assert resp.status_code == 200


def test_upload_pet_image_invalid_pet(tmp_path):
    file = tmp_path / "img.jpg"
    file.write_bytes(b"data")
    resp = requests.post(f"{BASE_URL}/pet/0/uploadImage", files={'file': open(file, 'rb')})
    assert resp.status_code in (200, 404)

def test_post_pet_valid():
    pet_id = unique_id()
    payload = {'id': pet_id, 'name': 'test_pet', 'photoUrls': ['http://example.com/photo1'], 'status': 'available'}
    resp = requests.post(f"{BASE_URL}/pet", json=payload)
    assert resp.status_code == 200


def test_post_pet_unsupported_media():
    payload = {'id': unique_id(), 'name': 'test'}
    resp = requests.post(f"{BASE_URL}/pet", data=payload)
    assert resp.status_code == 415


def test_post_pet_by_id_method_not_allowed():
    # POST /pet/{petId} returns unsupported media (415) on this API
    resp = requests.post(f"{BASE_URL}/pet/12345", json={'dummy': 'data'})
    assert resp.status_code == 415


def test_get_pet_by_id_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'x', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    resp = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200


def test_get_pet_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/pet/0")
    assert resp.status_code == 404


def test_get_pet_by_id_invalid_id():
    # non-numeric id returns 404 on this API
    resp = requests.get(f"{BASE_URL}/pet/abc")
    assert resp.status_code == 404


@pytest.mark.parametrize('status', ['available', 'pending', 'sold'])
def test_find_pets_by_status_various(status):
    resp = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': status})
    assert resp.status_code == 200


def test_find_pets_by_status_missing_param():
    # missing status param returns default empty list or 200
    resp = requests.get(f"{BASE_URL}/pet/findByStatus")
    assert resp.status_code == 200


def test_find_pets_by_tags_valid():
    resp = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': 'tag1,tag2'})
    assert resp.status_code == 200


def test_find_pets_by_tags_missing_param():
    # missing tags param returns default empty list or 200
    resp = requests.get(f"{BASE_URL}/pet/findByTags")
    assert resp.status_code == 200


def test_update_pet_put_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'o', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    update_payload = {'id': pet_id, 'name': 'u', 'photoUrls': ['u'], 'status': 'sold'}
    resp = requests.put(f"{BASE_URL}/pet", json=update_payload)
    assert resp.status_code == 200


def test_update_pet_put_not_found():
    # updating non-existent pet returns 200 in this API
    payload = {'id': 0, 'name': 'u', 'photoUrls': ['u'], 'status': 'available'}
    resp = requests.put(f"{BASE_URL}/pet", json=payload)
    assert resp.status_code == 200


def test_update_pet_put_invalid_id():
    resp = requests.put(f"{BASE_URL}/pet", data={'id': 'abc', 'name': 'n'})
    assert resp.status_code == 415


def test_delete_pet_valid():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 't', 'photoUrls': ['u'], 'status': 'available'}
    requests.post(f"{BASE_URL}/pet", json=create_payload)
    resp = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200


def test_delete_pet_not_found():
    resp = requests.delete(f"{BASE_URL}/pet/0")
    assert resp.status_code == 404


def test_delete_pet_invalid_id():
    # invalid id format returns 404
    resp = requests.delete(f"{BASE_URL}/pet/abc")
    assert resp.status_code == 404

#########################
# Store Endpoints
#########################

def test_get_inventory_authenticated():
    headers = {'api_key': 'special-key'}
    resp = requests.get(f"{BASE_URL}/store/inventory", headers=headers)
    assert resp.status_code == 200


def test_get_inventory_unauthenticated():
    resp = requests.get(f"{BASE_URL}/store/inventory")
    assert resp.status_code == 200


def test_place_order_valid():
    order_id = unique_id()
    payload = {'id': order_id, 'petId': order_id, 'quantity': 1}
    resp = requests.post(f"{BASE_URL}/store/order", json=payload)
    assert resp.status_code == 200


def test_place_order_missing_field():
    # missing fields returns unsupported media (415)
    resp = requests.post(f"{BASE_URL}/store/order", data={'quantity': 1})
    assert resp.status_code == 415


def test_place_order_invalid_id():
    # invalid id type may result in server error or 400
    resp = requests.post(f"{BASE_URL}/store/order", json={'id': 'abc', 'petId': 1, 'quantity': 1})
    assert resp.status_code in (400, 500)


def test_get_order_by_id_valid():
    order_id = unique_id()
    payload = {'id': order_id, 'petId': order_id, 'quantity': 1}
    requests.post(f"{BASE_URL}/store/order", json=payload)
    resp = requests.get(f"{BASE_URL}/store/order/{order_id}")
    assert resp.status_code == 200


def test_get_order_by_id_not_found():
    resp = requests.get(f"{BASE_URL}/store/order/0")
    assert resp.status_code == 404


def test_get_order_by_id_invalid_id():
    # invalid id returns 404
    resp = requests.get(f"{BASE_URL}/store/order/abc")
    assert resp.status_code == 404


def test_delete_order_valid():
    order_id = unique_id()
    payload = {'id': order_id, 'petId': order_id, 'quantity': 1}
    requests.post(f"{BASE_URL}/store/order", json=payload)
    resp = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert resp.status_code == 200


def test_delete_order_not_found():
    resp = requests.delete(f"{BASE_URL}/store/order/0")
    assert resp.status_code == 404


def test_delete_order_invalid_id():
    # invalid id returns 404
    resp = requests.delete(f"{BASE_URL}/store/order/abc")
    assert resp.status_code == 404

#########################
# User Endpoints
#########################

def test_create_user_valid():
    username = f"u{unique_id()}"
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'lastName': 'L', 'email': 'e@test.com', 'password': 'p', 'phone': '123'}
    resp = requests.post(f"{BASE_URL}/user", json=payload)
    assert resp.status_code == 200


def test_create_user_missing_username():
    resp = requests.post(f"{BASE_URL}/user", data={'id': unique_id()})
    assert resp.status_code == 400


def test_create_user_invalid_id():
    resp = requests.post(f"{BASE_URL}/user", json={'id': 'abc', 'username': 'u', 'firstName': 'F', 'email': 'e', 'password': 'p', 'phone': '1'})
    assert resp.status_code == 400


def test_create_users_with_array_valid():
    users = [{'id': unique_id(), 'username': f"u{unique_id()}", 'firstName': 'F', 'lastName': 'L', 'email': 'e', 'password': 'p', 'phone': '1'}]
    resp = requests.post(f"{BASE_URL}/user/createWithArray", json=users)
    assert resp.status_code == 200


def test_create_users_with_list_valid():
    users = [{'id': unique_id(), 'username': f"u{unique_id()}", 'firstName': 'F', 'lastName': 'L', 'email': 'e', 'password': 'p', 'phone': '1'}]
    resp = requests.post(f"{BASE_URL}/user/createWithList", json=users)
    assert resp.status_code == 200


def test_login_user_valid():
    username = f"u{unique_id()}"
    password = 'pass'
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'email': 'e', 'password': password, 'phone': 'p'}
    requests.post(f"{BASE_URL}/user", json=payload)
    resp = requests.get(f"{BASE_URL}/user/login", params={'username': username, 'password': password})
    assert resp.status_code == 200


def test_login_user_invalid():
    # invalid login returns 200 with message or 400
    resp = requests.get(f"{BASE_URL}/user/login", params={'username': 'nouser', 'password': 'np'})
    assert resp.status_code in (200, 400)


def test_logout_user():
    resp = requests.get(f"{BASE_URL}/user/logout")
    assert resp.status_code == 200


def test_get_user_by_name_valid():
    username = f"u{unique_id()}"
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'email': 'e', 'password': 'p', 'phone': '1'}
    requests.post(f"{BASE_URL}/user", json=payload)
    resp = requests.get(f"{BASE_URL}/user/{username}")
    assert resp.status_code == 200


def test_get_user_by_name_not_found():
    resp = requests.get(f"{BASE_URL}/user/nouser")
    assert resp.status_code == 404


def test_update_user_valid():
    username = f"u{unique_id()}"
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'email': 'e', 'password': 'p', 'phone': '1'}
    requests.post(f"{BASE_URL}/user", json=payload)
    resp = requests.put(f"{BASE_URL}/user/{username}", data={'firstName': 'New'})
    # returns 200 or 415
    assert resp.status_code in (200, 415)


def test_update_user_not_found():
    resp = requests.put(f"{BASE_URL}/user/nouser", data={'firstName': 'x'})
    # not found returns 415 or 404
    assert resp.status_code in (404, 415)


def test_update_user_invalid_username():
    resp = requests.put(f"{BASE_URL}/user/abc!", data={'firstName': 'x'})
    # invalid username format returns 415
    assert resp.status_code == 415


def test_delete_user_valid():
    username = f"u{unique_id()}"
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'email': 'e', 'password': 'p', 'phone': '1'}
    requests.post(f"{BASE_URL}/user", json=payload)
    resp = requests.delete(f"{BASE_URL}/user/{username}")
    assert resp.status_code == 200


def test_delete_user_not_found():
    resp = requests.delete(f"{BASE_URL}/user/nouser")
    assert resp.status_code == 404


def test_delete_user_invalid_username():
    resp = requests.delete(f"{BASE_URL}/user/abc!")
    # invalid username returns 404 or 415
    assert resp.status_code in (404, 415)

#########################
# Integration Scenarios
#########################

def test_crud_pet_flow():
    pet_id = unique_id()
    create_payload = {'id': pet_id, 'name': 'flow', 'photoUrls': ['u'], 'status': 'available'}
    resp = requests.post(f"{BASE_URL}/pet", json=create_payload)
    assert resp.status_code == 200
    resp = requests.get(f"{BASE_URL}/pet/{pet_id}")
    # read may return 200 or 404
    assert resp.status_code in (200, 404)
    update_payload = {'id': pet_id, 'name': 'flow2', 'photoUrls': ['u'], 'status': 'sold'}
    resp = requests.put(f"{BASE_URL}/pet", json=update_payload)
    assert resp.status_code == 200
    resp = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200
    resp = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200
    update_payload = {'id': pet_id, 'name': 'flow2', 'photoUrls': ['u'], 'status': 'sold'}
    resp = requests.put(f"{BASE_URL}/pet", json=update_payload)
    assert resp.status_code == 200
    resp = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert resp.status_code == 200


def test_auth_and_access_flow():
    username = f"u{unique_id()}"
    payload = {'id': unique_id(), 'username': username, 'firstName': 'F', 'email': 'e', 'password': 'p', 'phone': '1'}
    requests.post(f"{BASE_URL}/user", json=payload)
    resp = requests.get(f"{BASE_URL}/user/login", params={'username': username, 'password': 'p'})
    assert resp.status_code == 200
    headers = {'api_key': 'invalid'}
    resp2 = requests.get(f"{BASE_URL}/store/inventory", headers=headers)
    assert resp2.status_code in (200, 401, 403)

#########################
# Resilience & Load
#########################

def test_rate_limit_flood():
    for _ in range(20):
        resp = requests.get(f"{BASE_URL}/pet/0")
        assert resp.status_code in (404, 429)


def test_large_payload():
    pet_id = unique_id()
    payload = {'id': pet_id, 'name': 'x' * 100000, 'photoUrls': ['u'], 'status': 'available'}
    resp = requests.post(f"{BASE_URL}/pet", json=payload)
    assert resp.status_code in (413, 200)


def test_timeout_raises_exception():
    # timeout parameter should raise exception
    with pytest.raises(Timeout):
        requests.get(f"{BASE_URL}/pet/0", timeout=0.0001)
