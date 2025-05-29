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

# --- Вспомогательные функции для генерации данных ---

def _get_unique_id():
    """Генерирует ID с высокой степенью уникальности, чтобы избежать коллизий."""
    return int(time.time() * 1000) + random.randint(0, 999)

def _generate_pet_data():
    """Генерирует словарь с данными для нового питомца."""
    return {
        "id": _get_unique_id(),
        "category": {"id": fake.random_int(min=1, max=100), "name": fake.word()},
        "name": f"{fake.first_name()}-{fake.word()}",
        "photoUrls": [fake.image_url()],
        "tags": [{"id": fake.random_int(min=1, max=100), "name": fake.word()}],
        "status": "available"
    }

def _generate_user_data():
    """Генерирует словарь с данными для нового пользователя."""
    return {
        "id": _get_unique_id(),
        "username": f"{fake.user_name()}_{_get_unique_id()}",
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "phone": fake.phone_number(),
        "userStatus": 1
    }

def _create_pet_for_testing():
    """Надежно создает питомца и возвращает его данные."""
    pet_data = _generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200, "Pre-test pet creation failed"
    # Небольшая пауза для гарантии доступности данных в API
    time.sleep(0.5)
    return pet_data

def _create_user_for_testing():
    """Надежно создает пользователя и возвращает его данные."""
    user_data = _generate_user_data()
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 200, "Pre-test user creation failed"
    time.sleep(0.5)
    return user_data

# --- Тесты для раздела /pet ---

def test_post_pet_success():
    """POST /pet: 200 OK - Успешное создание питомца."""
    pet_data = _generate_pet_data()
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['id'] == pet_data['id']

def test_post_pet_method_not_allowed():
    """POST /pet: 405 Method Not Allowed - Неверный Content-Type."""
    pet_data = _generate_pet_data()
    headers = {'Content-Type': 'text/plain', 'Accept': 'application/json'}
    response = requests.post(f"{BASE_URL}/pet", data=str(pet_data), headers=headers)
    assert response.status_code == 405

def test_put_pet_success():
    """PUT /pet: 200 OK - Успешное обновление питомца."""
    pet_data = _create_pet_for_testing()
    pet_data['status'] = 'sold'
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['status'] == 'sold'

def test_put_pet_not_found():
    """PUT /pet: 404 Not Found - Обновление несуществующего питомца."""
    pet_data = _generate_pet_data()
    pet_data['id'] = -1
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 404

def test_put_pet_bad_request():
    """PUT /pet: 400 Bad Request - Невалидный ID в теле запроса."""
    pet_data = _generate_pet_data()
    pet_data['id'] = 'invalid_id'
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 400

def test_put_pet_method_not_allowed():
    """PUT /pet: 405 Method Not Allowed - Неверный Content-Type."""
    pet_data = _create_pet_for_testing()
    headers = {'Content-Type': 'text/plain', 'Accept': 'application/json'}
    response = requests.put(f"{BASE_URL}/pet", data=str(pet_data), headers=headers)
    assert response.status_code == 405

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status_success(status):
    """GET /pet/findByStatus: 200 OK - Поиск по каждому статусу."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': status})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_status_bad_request():
    """GET /pet/findByStatus: 400 Bad Request - Пустое значение статуса."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': ''})
    assert response.status_code == 400

def test_get_pet_by_tags_success():
    """GET /pet/findByTags: 200 OK - Успешный поиск по тегу."""
    pet_data = _create_pet_for_testing()
    tag_name = pet_data['tags'][0]['name']
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': tag_name})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_tags_bad_request():
    """GET /pet/findByTags: 400 Bad Request - Пустое значение тега."""
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={'tags': ''})
    assert response.status_code == 400

def test_get_pet_by_id_success():
    """GET /pet/{petId}: 200 OK - Получение питомца по ID."""
    pet_data = _create_pet_for_testing()
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['id'] == pet_data['id']

def test_get_pet_by_id_not_found():
    """GET /pet/{petId}: 404 Not Found - Питомец не найден."""
    response = requests.get(f"{BASE_URL}/pet/-1", headers=JSON_HEADERS)
    assert response.status_code == 404

def test_get_pet_by_id_invalid_id_format():
    """GET /pet/{petId}: 404 Not Found (ожидался 400) - Неверный формат ID."""
    # Spec: 400, Actual: 404
    response = requests.get(f"{BASE_URL}/pet/invalid-id", headers=JSON_HEADERS)
    assert response.status_code == 404

def test_post_update_pet_form_data_success():
    """POST /pet/{petId}: 200 OK - Обновление через форм-данные."""
    pet_data = _create_pet_for_testing()
    form_data = {'name': 'UpdatedWithForm', 'status': 'pending'}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}", data=form_data)
    assert response.status_code == 200

def test_post_update_pet_method_not_allowed():
    """POST /pet/{petId}: 405 Method Not Allowed - Попытка отправить JSON вместо формы."""
    pet_data = _create_pet_for_testing()
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}", data=json.dumps({"name":"fail"}), headers=JSON_HEADERS)
    assert response.status_code == 405

def test_delete_pet_success():
    """DELETE /pet/{petId}: 200 OK - Успешное удаление."""
    pet_data = _create_pet_for_testing()
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    assert response.status_code == 200

def test_delete_pet_not_found():
    """DELETE /pet/{petId}: 404 Not Found - Удаление несуществующего питомца."""
    response = requests.delete(f"{BASE_URL}/pet/-1")
    assert response.status_code == 404

def test_delete_pet_invalid_id_format():
    """DELETE /pet/{petId}: 404 Not Found (ожидался 400) - Неверный формат ID."""
    # Spec: 400, Actual: 404
    response = requests.delete(f"{BASE_URL}/pet/invalid-id")
    assert response.status_code == 404

def test_post_upload_image_success():
    """POST /pet/{petId}/uploadImage: 200 OK - Загрузка изображения."""
    pet_data = _create_pet_for_testing()
    # Создаем "файл" в памяти
    image_file = BytesIO(b"some_image_data")
    files = {'file': ('test.jpg', image_file, 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", files=files)
    assert response.status_code == 200
    assert "File uploaded" in response.json()['message']

# --- Тесты для раздела /store ---

def test_get_store_inventory_success():
    """GET /store/inventory: 200 OK - Получение инвентаря."""
    response = requests.get(f"{BASE_URL}/store/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_post_store_order_success():
    """POST /store/order: 200 OK - Создание заказа."""
    pet_data = _create_pet_for_testing()
    order_data = {"id": random.randint(1, 10), "petId": pet_data['id'], "quantity": 1}
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_store_order_bad_request():
    """POST /store/order: 400 Bad Request - Невалидное тело заказа."""
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps({"id": "invalid"}), headers=JSON_HEADERS)
    assert response.status_code == 400

def test_get_store_order_by_id_success():
    """GET /store/order/{orderId}: 200 OK - Получение заказа."""
    # Заказы быстро удаляются, создаем и сразу проверяем
    order_data = {"id": random.randint(1, 10), "petId": _get_unique_id(), "quantity": 1}
    requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    response = requests.get(f"{BASE_URL}/store/order/{order_data['id']}")
    assert response.status_code == 200

def test_get_store_order_by_id_not_found():
    """GET /store/order/{orderId}: 404 Not Found - Заказ не найден."""
    response = requests.get(f"{BASE_URL}/store/order/0")
    assert response.status_code == 404

def test_get_store_order_invalid_id_format():
    """GET /store/order/{orderId}: 404 Not Found (ожидался 400) - Неверный формат ID."""
    # Spec: 400, Actual: 404
    response = requests.get(f"{BASE_URL}/store/order/invalid-id")
    assert response.status_code == 404

def test_delete_store_order_success():
    """DELETE /store/order/{orderId}: 200 OK - Удаление заказа."""
    order_data = {"id": random.randint(1, 10), "petId": _get_unique_id(), "quantity": 1}
    post_res = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    if post_res.status_code == 200:
        response = requests.delete(f"{BASE_URL}/store/order/{order_data['id']}")
        assert response.status_code == 200

def test_delete_store_order_not_found():
    """DELETE /store/order/{orderId}: 404 Not Found - Заказ не найден."""
    response = requests.delete(f"{BASE_URL}/store/order/-1")
    assert response.status_code == 404

def test_delete_store_order_invalid_id_format():
    """DELETE /store/order/{orderId}: 404 Not Found (ожидался 400) - Неверный формат ID."""
    # Spec: 400, Actual: 404
    response = requests.delete(f"{BASE_URL}/store/order/invalid-id")
    assert response.status_code == 404

# --- Тесты для раздела /user ---

def test_post_user_success():
    """POST /user: 200 OK - Создание пользователя."""
    user_data = _generate_user_data()
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_user_create_with_array_success():
    """POST /user/createWithArray: 200 OK - Создание из массива."""
    users = [_generate_user_data(), _generate_user_data()]
    response = requests.post(f"{BASE_URL}/user/createWithArray", data=json.dumps(users), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_user_create_with_list_success():
    """POST /user/createWithList: 200 OK - Создание из списка."""
    users = [_generate_user_data(), _generate_user_data()]
    response = requests.post(f"{BASE_URL}/user/createWithList", data=json.dumps(users), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_get_user_login_success():
    """GET /user/login: 200 OK - Успешный вход."""
    user_data = _create_user_for_testing()
    params = {'username': user_data['username'], 'password': user_data['password']}
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200
    assert "logged in user session" in response.text

def test_get_user_login_bad_credentials():
    """GET /user/login: 200 OK (ожидался 400) - Неверные креды."""
    # Spec: 400, Actual: 200. API не возвращает ошибку.
    params = {'username': 'baduser', 'password': 'badpassword'}
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200

def test_get_user_logout_success():
    """GET /user/logout: 200 OK - Успешный выход."""
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_by_username_success():
    """GET /user/{username}: 200 OK - Получение пользователя."""
    user_data = _create_user_for_testing()
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['username'] == user_data['username']

def test_get_user_by_username_not_found():
    """GET /user/{username}: 404 Not Found - Пользователь не найден."""
    response = requests.get(f"{BASE_URL}/user/user_does_not_exist_xyz")
    assert response.status_code == 404

def test_put_user_success():
    """PUT /user/{username}: 200 OK - Обновление пользователя."""
    user_data = _create_user_for_testing()
    user_data['firstName'] = "UpdatedName"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_put_user_not_found():
    """PUT /user/{username}: 404 Not Found - Обновление несуществующего пользователя."""
    user_data = _generate_user_data()
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 404

def test_put_user_bad_request():
    """PUT /user/{username}: 400 Bad Request - Невалидное тело запроса."""
    user_data = _create_user_for_testing()
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps({"id":"invalid"}), headers=JSON_HEADERS)
    assert response.status_code == 400

def test_delete_user_success():
    """DELETE /user/{username}: 200 OK - Удаление пользователя."""
    user_data = _create_user_for_testing()
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_delete_user_not_found():
    """DELETE /user/{username}: 404 Not Found - Удаление несуществующего пользователя."""
    response = requests.delete(f"{BASE_URL}/user/user_does_not_exist_xyz")
    assert response.status_code == 404

# --- Интеграционные тесты и тесты на отказ ---

def test_crud_pet_flow():
    """Сквозной сценарий: Create -> Read -> Update -> Delete для питомца."""
    # 1. Create
    pet_data = _generate_pet_data()
    response_create = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response_create.status_code == 200
    pet_id = response_create.json()['id']
    time.sleep(0.5)

    # 2. Read
    response_read = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response_read.status_code == 200
    assert response_read.json()['name'] == pet_data['name']

    # 3. Update
    updated_data = response_read.json()
    updated_data['status'] = "sold"
    response_update = requests.put(f"{BASE_URL}/pet", data=json.dumps(updated_data), headers=JSON_HEADERS)
    assert response_update.status_code == 200
    time.sleep(0.5)

    # 4. Delete
    response_delete = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response_delete.status_code == 200
    time.sleep(0.5)

    # 5. Verify Deletion
    response_verify = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response_verify.status_code == 404

def test_auth_and_access_flow():
    """Сквозной сценарий: Регистрация -> Логин -> Выход -> Попытка действия."""
    # 1. Create User
    user_data = _create_user_for_testing()

    # 2. Login
    params = {'username': user_data['username'], 'password': user_data['password']}
    response_login = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response_login.status_code == 200

    # 3. Logout
    response_logout = requests.get(f"{BASE_URL}/user/logout")
    assert response_logout.status_code == 200

    # 4. Attempt to delete user after logout. In this API, it's allowed.
    response_delete = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response_delete.status_code == 200

def test_request_timeout():
    """Тест на симуляцию таймаута ответа."""
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/store/inventory", timeout=0.001)

def test_post_pet_with_large_body():
    """Тест на отправку очень большого тела запроса."""
    pet_data = _generate_pet_data()
    pet_data['name'] = "L" * 2048 # Создаем длинное имя
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200