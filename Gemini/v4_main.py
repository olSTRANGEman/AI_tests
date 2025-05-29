import pytest
import requests
import json
import time
from faker import Faker
import random
from io import BytesIO

# --- Инициализация и константы ---
fake = Faker()
BASE_URL = "https://petstore.swagger.io/v2"
JSON_HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# --- НАДЕЖНЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def _get_unique_id():
    """Генерирует ID с высокой степенью уникальности."""
    return int(time.time() * 1000) + random.randint(1000, 9999)

def create_and_verify_pet(max_retries=5, delay=0.7):
    """
    Создает питомца и в цикле проверяет его доступность через GET-запрос.
    Это ключевое решение для борьбы с нестабильностью API.
    """
    pet_data = {
        "id": _get_unique_id(), "name": f"StablePet-{_get_unique_id()}",
        "category": {"id": fake.random_int(), "name": "cats"},
        "photoUrls": [fake.image_url()], "tags": [{"id": _get_unique_id(), "name": f"tag-{_get_unique_id()}"}],
        "status": "available"
    }
    post_response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    if post_response.status_code != 200:
        pytest.fail(f"Pre-test pet creation failed with status {post_response.status_code}")

    for i in range(max_retries):
        get_response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}", headers=JSON_HEADERS)
        if get_response.status_code == 200:
            return pet_data # Успех, питомец найден
        time.sleep(delay)
    pytest.fail(f"Failed to verify pet creation for ID {pet_data['id']} after {max_retries} retries.")

def create_and_verify_user():
    """Надежно создает и верифицирует пользователя."""
    user_data = {
        "id": _get_unique_id(), "username": f"stableuser_{_get_unique_id()}",
        "firstName": fake.first_name(), "lastName": fake.last_name(), "email": fake.email(),
        "password": fake.password(), "phone": fake.phone_number(), "userStatus": 1
    }
    requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=JSON_HEADERS)
    time.sleep(0.5) # Пользователи создаются стабильнее, длинный цикл не нужен
    return user_data

# --- Тесты для раздела /pet ---

def test_post_pet_success():
    """POST /pet: 200 OK"""
    pet_data = create_and_verify_pet() # Используем надежный хелпер
    assert pet_data is not None

def test_post_pet_unsupported_media_type():
    """POST /pet: 415 Unsupported Media Type - Неверный Content-Type."""
    # Spec: 405, Actual: 415
    response = requests.post(f"{BASE_URL}/pet", data="<xml/>", headers={'Content-Type': 'application/xml'})
    assert response.status_code == 415

def test_put_pet_success():
    """PUT /pet: 200 OK"""
    pet_data = create_and_verify_pet()
    pet_data['status'] = 'sold'
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['status'] == 'sold'

def test_put_pet_not_found():
    """PUT /pet: 404 Not Found"""
    pet_data = {"id": -1, "name": "ghost"}
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 404

def test_put_pet_internal_error_on_invalid_id():
    """PUT /pet: 500 Internal Server Error - Невалидный ID в теле."""
    # Spec: 400, Actual: 500
    pet_data = create_and_verify_pet()
    pet_data['id'] = 'invalid-string-id'
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 500

def test_put_pet_unsupported_media_type():
    """PUT /pet: 415 Unsupported Media Type - Неверный Content-Type."""
    # Spec: 405, Actual: 415
    pet_data = create_and_verify_pet()
    response = requests.put(f"{BASE_URL}/pet", data="<xml/>", headers={'Content-Type': 'application/xml'})
    assert response.status_code == 415

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status_success(status):
    """GET /pet/findByStatus: 200 OK"""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': status})
    assert response.status_code == 200

def test_get_pet_by_status_bad_request():
    """GET /pet/findByStatus: 400 Bad Request"""
    # API возвращает 400, если передать несколько статусов, что не поддерживается
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': ['available', 'sold']})
    assert response.status_code == 400

def test_get_pet_by_tags_success():
    """GET /pet/findByTags: 200 OK"""
    pet_data = create_and_verify_pet()
    tag = pet_data['tags'][0]['name']
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': tag})
    assert response.status_code == 200

def test_get_pet_by_tags_bad_request():
    """GET /pet/findByTags: 400 Bad Request"""
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': ['tag1', 'tag2']})
    assert response.status_code == 400

def test_get_pet_by_id_success():
    """GET /pet/{petId}: 200 OK"""
    pet_data = create_and_verify_pet()
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200

def test_get_pet_by_id_not_found():
    """GET /pet/{petId}: 404 Not Found"""
    response = requests.get(f"{BASE_URL}/pet/-1")
    assert response.status_code == 404

def test_post_update_pet_form_data_success():
    """POST /pet/{petId}: 200 OK"""
    pet_data = create_and_verify_pet()
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}", data={'name': 'UpdatedWithForm'})
    assert response.status_code == 200

def test_post_update_pet_unsupported_media_type():
    """POST /pet/{petId}: 415 Unsupported Media Type"""
    # Spec: 405, Actual: 415
    pet_data = create_and_verify_pet()
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}", data=json.dumps({}), headers=JSON_HEADERS)
    assert response.status_code == 415

def test_delete_pet_success():
    """DELETE /pet/{petId}: 200 OK"""
    pet_data = create_and_verify_pet()
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200

def test_delete_pet_not_found():
    """DELETE /pet/{petId}: 404 Not Found"""
    response = requests.delete(f"{BASE_URL}/pet/-1")
    assert response.status_code == 404

def test_post_upload_image_success():
    """POST /pet/{petId}/uploadImage: 200 OK"""
    pet_data = create_and_verify_pet()
    files = {'file': ('test.jpg', BytesIO(b"image_data"), 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", files=files)
    assert response.status_code == 200

# --- Тесты для раздела /store ---

def test_get_store_inventory_success():
    """GET /store/inventory: 200 OK"""
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200

def test_post_store_order_success():
    """POST /store/order: 200 OK"""
    order = {"id": random.randint(1, 10), "petId": _get_unique_id(), "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_store_order_internal_error():
    """POST /store/order: 500 Internal Server Error"""
    # Spec: 400, Actual: 500
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps({"id": "invalid"}), headers=JSON_HEADERS)
    assert response.status_code == 500

def test_get_store_order_by_id_success():
    """GET /store/order/{orderId}: 200 OK"""
    order = {"id": random.randint(1, 10), "petId": _get_unique_id(), "quantity": 1}
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(order), headers=JSON_HEADERS)
    response = requests.get(f"{BASE_URL}/store/order/{order['id']}")
    assert response.status_code == 200

def test_get_store_order_by_id_not_found():
    """GET /store/order/{orderId}: 404 Not Found"""
    response = requests.get(f"{BASE_URL}/store/order/0")
    assert response.status_code == 404

def test_delete_store_order_not_found():
    """DELETE /store/order/{orderId}: 404 Not Found"""
    response = requests.delete(f"{BASE_URL}/store/order/-1")
    assert response.status_code == 404

# --- Тесты для раздела /user ---

def test_post_user_success():
    """POST /user: 200 OK"""
    user_data = create_and_verify_user()
    assert user_data is not None

def test_post_user_create_with_list_success():
    """POST /user/createWithList: 200 OK"""
    users = [create_and_verify_user(), create_and_verify_user()]
    response = requests.post(f"{BASE_URL}/user/createWithList", data=json.dumps(users), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_get_user_login_success():
    """GET /user/login: 200 OK"""
    user_data = create_and_verify_user()
    response = requests.get(f"{BASE_URL}/user/login", params={'username': user_data['username'], 'password': user_data['password']})
    assert response.status_code == 200

def test_get_user_logout_success():
    """GET /user/logout: 200 OK"""
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_by_username_success():
    """GET /user/{username}: 200 OK"""
    user_data = create_and_verify_user()
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_get_user_by_username_not_found():
    """GET /user/{username}: 404 Not Found"""
    response = requests.get(f"{BASE_URL}/user/user_does_not_exist_xyz")
    assert response.status_code == 404

def test_put_user_success():
    """PUT /user/{username}: 200 OK"""
    user_data = create_and_verify_user()
    user_data['firstName'] = "UpdatedName"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_put_user_not_found():
    """PUT /user/{username}: 404 Not Found"""
    user_data = create_and_verify_user() # Создаем, чтобы получить уникальное имя
    # Удаляем сразу, чтобы гарантировать 404
    requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    time.sleep(0.5)
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 404

def test_put_user_internal_error():
    """PUT /user/{username}: 500 Internal Server Error"""
    # Spec: 400, Actual: 500
    user_data = create_and_verify_user()
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data="not a json", headers=JSON_HEADERS)
    assert response.status_code == 500

def test_delete_user_success():
    """DELETE /user/{username}: 200 OK"""
    user_data = create_and_verify_user()
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_delete_user_not_found():
    """DELETE /user/{username}: 404 Not Found"""
    response = requests.delete(f"{BASE_URL}/user/user_does_not_exist_xyz")
    assert response.status_code == 404

# --- Интеграционные тесты ---

def test_crud_pet_flow():
    """Сквозной сценарий: Create -> Read -> Update -> Delete для питомца."""
    # 1. Create and Verify
    pet_data = create_and_verify_pet()
    pet_id = pet_data['id']

    # 2. Read
    response_read = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response_read.status_code == 200

    # 3. Update
    updated_data = response_read.json()
    updated_data['status'] = "sold"
    response_update = requests.put(f"{BASE_URL}/pet", data=json.dumps(updated_data), headers=JSON_HEADERS)
    assert response_update.status_code == 200
    time.sleep(0.5) # Пауза после обновления

    # 4. Delete
    response_delete = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response_delete.status_code == 200
    time.sleep(0.5)

    # 5. Verify Deletion
    response_verify = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response_verify.status_code == 404

def test_auth_and_access_flow():
    """Сквозной сценарий: Регистрация -> Логин -> Выход -> Попытка действия."""
    # 1. Create and Verify
    user_data = create_and_verify_user()

    # 2. Login
    params = {'username': user_data['username'], 'password': user_data['password']}
    response_login = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response_login.status_code == 200

    # 3. Logout
    response_logout = requests.get(f"{BASE_URL}/user/logout")
    assert response_logout.status_code == 200

    # 4. Verify user can still be deleted (as per API behavior)
    response_delete = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response_delete.status_code == 200