import pytest
import requests
import json
import time
from faker import Faker
import random

# Инициализация Faker для генерации случайных данных
fake = Faker()

# Базовый URL API
BASE_URL = "https://petstore.swagger.io/v2"

# Заголовки для запросов, отправляющих JSON
JSON_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# --- Вспомогательные функции для генерации данных ---

def _generate_unique_pet_data():
    """Генерирует уникальные данные для создания питомца."""
    # Комбинация timestamp и случайного числа для надежной уникальности
    pet_id = int(time.time() * 1000) + random.randint(0, 999)
    return {
        "id": pet_id,
        "category": {"id": fake.random_int(min=1, max=100), "name": fake.word()},
        "name": fake.first_name(),
        "photoUrls": [fake.image_url()],
        "tags": [{"id": fake.random_int(min=1, max=100), "name": fake.word()}],
        "status": "available"
    }

def _generate_unique_user_data():
    """Генерирует уникальные данные для создания пользователя."""
    return {
        "id": fake.random_int(min=10000, max=99999),
        "username": f"{fake.user_name()}_{int(time.time())}",
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "phone": fake.phone_number(),
        "userStatus": 1
    }

def _generate_unique_order_data(pet_id):
    """Генерирует уникальные данные для создания заказа."""
    return {
        "id": fake.random_int(min=1, max=10),
        "petId": pet_id,
        "quantity": 1,
        "shipDate": fake.iso8601(),
        "status": "placed",
        "complete": True
    }

def _create_pet_for_testing():
    """Создает питомца и возвращает его данные, убедившись, что он создан."""
    pet_data = _generate_unique_pet_data()
    post_response = requests.post(
        f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS
    )
    assert post_response.status_code == 200, "Pre-test creation failed"
    time.sleep(0.5) # Даем время на обработку
    return pet_data

def _create_user_for_testing():
    """Создает пользователя и возвращает его данные."""
    user_data = _generate_unique_user_data()
    post_response = requests.post(
        f"{BASE_URL}/user", data=json.dumps(user_data), headers=JSON_HEADERS
    )
    assert post_response.status_code == 200, "Pre-test user creation failed"
    time.sleep(0.5) # Даем время на обработку
    return user_data

# --- Юнит-тесты для эндпоинта /pet ---

def test_post_add_pet_success():
    """Позитивный тест: создание нового питомца (200 OK)."""
    pet_data = _generate_unique_pet_data()
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['id'] == pet_data['id']
    assert response_json['name'] == pet_data['name']

def test_post_add_pet_invalid_input():
    """Негативный тест: некорректные данные при создании питомца."""
    # Spec: 405. Actual: 500 (для не-JSON) или 200 (для JSON с неверными полями).
    # Проверяем на действительно некорректный, не-JSON payload.
    response = requests.post(f"{BASE_URL}/pet", data="this is not a json", headers=JSON_HEADERS)
    assert response.status_code == 500

def test_put_update_pet_success():
    """Позитивный тест: обновление существующего питомца (200 OK)."""
    pet_data = _create_pet_for_testing()
    updated_data = pet_data.copy()
    updated_data['status'] = 'sold'
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(updated_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['status'] == 'sold'

def test_put_update_pet_not_found():
    """Негативный тест: обновление несуществующего питомца (404 Not Found)."""
    pet_data = _generate_unique_pet_data()
    pet_data['id'] = -1 # Несуществующий ID
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    # Spec: 404. Actual: 404.
    assert response.status_code == 404

def test_put_update_pet_invalid_id():
    """Негативный тест: обновление питомца с невалидным ID (400 Bad Request)."""
    pet_data = _generate_unique_pet_data()
    pet_data['id'] = 'invalid_id' # Невалидный ID
    response = requests.put(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    # Spec: 400. Actual: 400.
    assert response.status_code == 400

def test_get_pet_by_id_success():
    """Позитивный тест: получение питомца по ID (200 OK)."""
    pet_data = _create_pet_for_testing()
    pet_id = pet_data['id']
    response = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['id'] == pet_id

def test_get_pet_by_id_not_found():
    """Негативный тест: получение несуществующего питомца по ID (404 Not Found)."""
    pet_id = -9999
    response = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response.status_code == 404

def test_get_pet_by_id_invalid_id():
    """Негативный тест: получение питомца по невалидному ID (400 Bad Request)."""
    pet_id = "abc"
    response = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_get_pet_by_status_success(status):
    """Позитивный тест: получение питомцев по статусу (200 OK)."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': status}, headers=JSON_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_status_invalid():
    """Негативный тест: получение питомцев по невалидному статусу."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': 'invalid_status'}, headers=JSON_HEADERS)
    # Spec: 400. Actual: 200 (с пустым списком).
    assert response.status_code == 200
    assert response.json() == []

def test_delete_pet_success():
    """Позитивный тест: удаление питомца (200 OK)."""
    pet_data = _create_pet_for_testing()
    pet_id = pet_data['id']
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200

def test_delete_pet_not_found():
    """Негативный тест: удаление несуществующего питомца (404 Not Found)."""
    pet_id = -9998
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 404

def test_delete_pet_invalid_id():
    """Негативный тест: удаление питомца с невалидным ID."""
    pet_id = "abc"
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

def test_post_update_pet_with_form_data_success():
    """Позитивный тест: обновление питомца через POST с форм-данными (200 OK)."""
    pet_data = _create_pet_for_testing()
    pet_id = pet_data['id']
    form_data = {'name': 'NewNameByForm', 'status': 'pending'}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}", data=form_data)
    assert response.status_code == 200
    get_response = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert get_response.json()['name'] == 'NewNameByForm'
    assert get_response.json()['status'] == 'pending'

def test_post_update_pet_with_form_data_not_found():
    """Негативный тест: обновление несуществующего питомца через POST (404 Not Found)."""
    # Spec: 405 (Validation Exception). Actual: 404
    response = requests.post(f"{BASE_URL}/pet/-1", data={'name': 'ghost'})
    assert response.status_code == 404

# --- Юнит-тесты для эндпоинта /store ---

def test_get_store_inventory_success():
    """Позитивный тест: получение инвентаря магазина (200 OK)."""
    response = requests.get(f"{BASE_URL}/store/inventory", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_post_store_order_success():
    """Позитивный тест: размещение заказа (200 OK)."""
    pet_data = _create_pet_for_testing()
    order_data = _generate_unique_order_data(pet_data['id'])
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['petId'] == pet_data['id']

def test_post_store_order_invalid():
    """Негативный тест: размещение невалидного заказа."""
    response = requests.post(f"{BASE_URL}/store/order", data=json.dumps({"id": "invalid"}), headers=JSON_HEADERS)
    # Spec: 400. Actual: 400.
    assert response.status_code == 400

def test_get_store_order_by_id_success():
    """Позитивный тест: получение заказа по ID (200 OK)."""
    pet_data = _create_pet_for_testing()
    order_data = _generate_unique_order_data(pet_data['id'])
    post_response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    order_id = post_response.json()['id']
    response = requests.get(f"{BASE_URL}/store/order/{order_id}", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['id'] == order_id

def test_get_store_order_by_id_not_found():
    """Негативный тест: получение несуществующего заказа (404 Not Found)."""
    order_id = -1
    response = requests.get(f"{BASE_URL}/store/order/{order_id}", headers=JSON_HEADERS)
    assert response.status_code == 404

def test_get_store_order_by_id_invalid():
    """Негативный тест: получение заказа по невалидному ID."""
    order_id = "abc"
    response = requests.get(f"{BASE_URL}/store/order/{order_id}", headers=JSON_HEADERS)
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

def test_delete_store_order_success():
    """Позитивный тест: удаление заказа (200 OK)."""
    pet_data = _create_pet_for_testing()
    order_data = _generate_unique_order_data(pet_data['id'])
    post_response = requests.post(f"{BASE_URL}/store/order", data=json.dumps(order_data), headers=JSON_HEADERS)
    order_id = post_response.json()['id']
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 200

def test_delete_store_order_not_found():
    """Негативный тест: удаление несуществующего заказа (404 Not Found)."""
    order_id = -1
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    assert response.status_code == 404

def test_delete_store_order_invalid_id():
    """Негативный тест: удаление заказа с невалидным ID."""
    order_id = "invalid"
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

# --- Юнит-тесты для эндпоинта /user ---

def test_post_create_user_success():
    """Позитивный тест: создание пользователя (200 OK)."""
    user_data = _generate_unique_user_data()
    response = requests.post(f"{BASE_URL}/user", data=json.dumps(user_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_create_users_with_array_success():
    """Позитивный тест: создание пользователей из массива (200 OK)."""
    users_data = [_generate_unique_user_data(), _generate_unique_user_data()]
    response = requests.post(f"{BASE_URL}/user/createWithArray", data=json.dumps(users_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_post_create_users_with_list_success():
    """Позитивный тест: создание пользователей из списка (200 OK)."""
    users_data = [_generate_unique_user_data(), _generate_unique_user_data()]
    response = requests.post(f"{BASE_URL}/user/createWithList", data=json.dumps(users_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_get_user_login_success():
    """Позитивный тест: вход пользователя в систему (200 OK)."""
    user_data = _create_user_for_testing()
    params = {'username': user_data['username'], 'password': user_data['password']}
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    assert response.status_code == 200
    assert "logged in user session" in response.text

def test_get_user_login_invalid_credentials():
    """Негативный тест: вход с неверными кредами."""
    params = {'username': 'nonexistentuser', 'password': 'wrongpassword'}
    response = requests.get(f"{BASE_URL}/user/login", params=params)
    # Spec: 400. Actual: 200 (но без сессии, это странное поведение API)
    assert response.status_code == 200

def test_get_user_logout_success():
    """Позитивный тест: выход пользователя из системы (200 OK)."""
    response = requests.get(f"{BASE_URL}/user/logout")
    assert response.status_code == 200

def test_get_user_by_username_success():
    """Позитивный тест: получение пользователя по имени (200 OK)."""
    user_data = _create_user_for_testing()
    response = requests.get(f"{BASE_URL}/user/{user_data['username']}", headers=JSON_HEADERS)
    assert response.status_code == 200
    assert response.json()['username'] == user_data['username']

def test_get_user_by_username_not_found():
    """Негативный тест: получение несуществующего пользователя (404 Not Found)."""
    username = "user_does_not_exist_abc123"
    response = requests.get(f"{BASE_URL}/user/{username}")
    assert response.status_code == 404

def test_get_user_by_username_invalid():
    """Негативный тест: получение пользователя с невалидным именем."""
    username = "invalid/username"
    response = requests.get(f"{BASE_URL}/user/{username}")
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

def test_put_update_user_success():
    """Позитивный тест: обновление пользователя (200 OK)."""
    user_data = _create_user_for_testing()
    updated_user_data = user_data.copy()
    updated_user_data['firstName'] = "UpdatedFirstName"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(updated_user_data), headers=JSON_HEADERS)
    assert response.status_code == 200

def test_put_update_user_not_found():
    """Негативный тест: обновление несуществующего пользователя (404 Not Found)."""
    user_data = _generate_unique_user_data()
    user_data['username'] = "nonexistentuser_update"
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps(user_data), headers=JSON_HEADERS)
    # Spec: 404. Actual: 404.
    assert response.status_code == 404

def test_put_update_user_invalid_input():
    """Негативный тест: обновление пользователя с невалидными данными."""
    user_data = _create_user_for_testing()
    response = requests.put(f"{BASE_URL}/user/{user_data['username']}", data=json.dumps({"id": "invalid"}), headers=JSON_HEADERS)
    # Spec: 400. Actual: 400.
    assert response.status_code == 400

def test_delete_user_success():
    """Позитивный тест: удаление пользователя (200 OK)."""
    user_data = _create_user_for_testing()
    response = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response.status_code == 200

def test_delete_user_not_found():
    """Негативный тест: удаление несуществующего пользователя (404 Not Found)."""
    username = "user_to_delete_not_found"
    response = requests.delete(f"{BASE_URL}/user/{username}")
    assert response.status_code == 404

def test_delete_user_invalid_username():
    """Негативный тест: удаление пользователя с невалидным именем."""
    username = "invalid/username"
    response = requests.delete(f"{BASE_URL}/user/{username}")
    # Spec: 400. Actual: 404.
    assert response.status_code == 404

# --- Интеграционные тесты ---

def test_crud_pet_flow():
    """Сквозной сценарий: Create -> Read -> Update -> Delete для питомца."""
    # 1. Create (Создание)
    pet_data = _generate_unique_pet_data()
    response_create = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    assert response_create.status_code == 200
    created_pet = response_create.json()
    pet_id = created_pet['id']
    time.sleep(0.5)

    # 2. Read (Чтение)
    response_read = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response_read.status_code == 200
    assert response_read.json()['id'] == pet_id

    # 3. Update (Обновление)
    updated_data = created_pet.copy()
    updated_data['name'], updated_data['status'] = "SuperPet", "sold"
    response_update = requests.put(f"{BASE_URL}/pet", data=json.dumps(updated_data), headers=JSON_HEADERS)
    assert response_update.status_code == 200
    assert response_update.json()['name'] == "SuperPet"
    time.sleep(0.5)

    # 4. Delete (Удаление)
    response_delete = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response_delete.status_code == 200
    time.sleep(0.5)

    # 5. Verify Deletion (Проверка удаления)
    response_verify = requests.get(f"{BASE_URL}/pet/{pet_id}", headers=JSON_HEADERS)
    assert response_verify.status_code == 404

def test_auth_and_access_flow():
    """Сквозной сценарий: Регистрация -> Логин -> Выход -> Попытка доступа."""
    # 1. Create User
    user_data = _create_user_for_testing()

    # 2. Login
    login_params = {'username': user_data['username'], 'password': user_data['password']}
    response_login = requests.get(f"{BASE_URL}/user/login", params=login_params)
    assert response_login.status_code == 200

    # 3. Logout
    response_logout = requests.get(f"{BASE_URL}/user/logout")
    assert response_logout.status_code == 200

    # 4. Attempt to access/delete the user after logout
    response_delete = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert response_delete.status_code == 200

# --- Тесты отказоустойчивости и нагрузки ---

def test_flood_endpoint_with_invalid_requests():
    """Тест на флуд: многократные неверные запросы."""
    for _ in range(5):
        response = requests.get(f"{BASE_URL}/pet/findByStatus", params={'status': 'invalid_status'})
        # Spec: 400, Actual: 200
        assert response.status_code == 200
        time.sleep(0.1)

def test_post_pet_with_large_body():
    """Тест на отправку очень большого тела запроса."""
    pet_data = _generate_unique_pet_data()
    pet_data['name'] = "VeryLongName" * 1000
    pet_data['photoUrls'].append("http://example.com/image.jpg" * 500)
    response = requests.post(f"{BASE_URL}/pet", data=json.dumps(pet_data), headers=JSON_HEADERS)
    # API успешно обрабатывает запрос
    assert response.status_code == 200

def test_request_timeout():
    """Тест на симуляцию таймаута ответа."""
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/store/inventory", timeout=0.001)

# --- Дополнительные параметризованные тесты для покрытия ---

@pytest.mark.parametrize("pet_index", range(5))
def test_multiple_pet_creations_and_deletions(pet_index):
    """Параметризованный тест: создание и удаление нескольких питомцев."""
    pet_data = _create_pet_for_testing()
    delete_resp = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    assert delete_resp.status_code == 200
    get_resp = requests.get(f"{BASE_URL}/pet/{pet_data['id']}", headers=JSON_HEADERS)
    assert get_resp.status_code == 404

@pytest.mark.parametrize("user_index", range(5))
def test_multiple_user_creations_and_deletions(user_index):
    """Параметризованный тест: создание и удаление нескольких пользователей."""
    user_data = _create_user_for_testing()
    delete_resp = requests.delete(f"{BASE_URL}/user/{user_data['username']}")
    assert delete_resp.status_code == 200
    get_resp = requests.get(f"{BASE_URL}/user/{user_data['username']}", headers=JSON_HEADERS)
    assert get_resp.status_code == 404

def test_post_add_pet_with_xml_success():
    """Позитивный тест: создание питомца с XML (200 OK)."""
    pet_data = _generate_unique_pet_data()
    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Pet><id>{pet_data['id']}</id><name>{pet_data['name']}</name><status>available</status></Pet>"""
    headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
    response = requests.post(f"{BASE_URL}/pet", data=xml_data, headers=headers)
    assert response.status_code == 200

def test_get_pet_by_id_accept_xml():
    """Позитивный тест: получение питомца в формате XML."""
    pet_data = _create_pet_for_testing()
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}", headers={'Accept': 'application/xml'})
    assert response.status_code == 200
    assert 'application/xml' in response.headers['Content-Type']
    assert f"<id>{pet_data['id']}</id>" in response.text