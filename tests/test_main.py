import uuid

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


@pytest.fixture(scope="function")
def menu_id():
    data = {
        'title': f'NEW_TITLE_MENU_PYTEST_{uuid.uuid4()}',
        'description': f'NEW_DESCRIPTION_MENU_PYTEST_{uuid.uuid4()}'
    }
    response = client.post('/api/v1/menus', json=data)
    assert response.status_code == 201
    return response.json()['id']


@pytest.fixture(scope="function")
def submenu_id(menu_id):
    data = {
        'title': f'NEW_TITLE_SUBMENU_PYTEST_{uuid.uuid4()}',
        'description': f'NEW_DESCRIPTION_SUBMENU_PYTEST_{uuid.uuid4()}'
    }
    response = client.post(f'/api/v1/menus/{menu_id}/submenus/', json=data)
    assert response.status_code == 201
    return response.json()['id']


@pytest.fixture(scope="function")
def dish_id(menu_id, submenu_id):
    data = {
        'price': '3.99',
        'title': 'New Dish Title2',
        'description': 'New Dish Description2'
    }
    response = client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=data
    )
    assert response.status_code == 201
    assert response.json()['price'] == data['price']
    assert response.json()['title'] == data['title']
    assert response.json()['description'] == data['description']
    return response.json()['id']


class TestMenu:
    base_url = 'http://localhost:8000'
    url = 'api/v1/menus'

    # Просматривает список меню
    def test_get_list_menu(self):
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.json() == [], 'JSON-ответ не пустой, ожидался пустой список'

    # Создает меню
    def test_create_menu(self):
        data = {
            'title': f'NEW_TITLE_MENU_PYTEST_{uuid.uuid4()}',
            'description': f'NEW_DESCRIPTION_MENU_PYTEST_{uuid.uuid4()}'
        }
        response = client.post(self.url, json=data)

        assert response.status_code == 201
        assert response.json()['title'] == data['title']
        assert response.json()['description'] == data['description']
        assert 'submenus_count' in response.json() and (
            response.json()['submenus_count'] == 0
        )
        assert 'dishes_count' in response.json() and (
            response.json()['dishes_count'] == 0
        )

    # Просматривает список меню
    def test_get_list_menu_not_empty(self, menu_id):
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.json() != [], 'JSON-ответ пустой, ожидался непустой список'

    # Просматривает определенное меню
    def test_get_target_menu(self, menu_id):
        assert menu_id is not None, 'ID меню не был сохранен'
        response = client.get(f'/{self.url}/{menu_id}')

        assert response.status_code == 200
        assert response.json()['id'] == menu_id

    # Обновляет меню
    def test_update_current_menu(self, menu_id):
        assert menu_id is not None, 'ID меню не был сохранен'

        updated_data = {
            'title': f'Updated Test Menu_{uuid.uuid4()}',
            'description': f'Updated Test Menu Description_{uuid.uuid4()}'
        }

        response = client.patch(f'/{self.url}/{menu_id}', json=updated_data)
        assert response.status_code == 200
        assert response.json()['title'] == updated_data['title']
        assert response.json()['description'] == updated_data['description']
        assert 'submenus_count' in response.json() and (
            response.json()['submenus_count'] == 0
        )
        assert 'dishes_count' in response.json() and (
            response.json()['dishes_count'] == 0
        )

    # Удаляет созданное меню
    def test_delete_menu(self, menu_id):
        assert menu_id is not None, 'ID меню не был сохранен'

        response = client.delete(f'/{self.url}/{menu_id}')
        assert response.status_code == 200

        response = client.get(f'/{self.url}/{menu_id}')
        assert response.status_code == 404, 'Ошибка 404'


class TestSubmenu:
    base_url = 'http://localhost:8000'
    url = 'api/v1/menus'

    # Просмотр списка подменю
    def test_get_list_all_submenus(self, menu_id):
        response = client.get(f'/{self.url}/{menu_id}/submenus/')
        assert response.status_code == 200
        assert response.json() == [], 'JSON-ответ не пустой, ожидался пустой список'

    # Создать подменю
    def test_create_submenu(self, menu_id):
        data = {
            'title': f'NEW_TITLE_SUBMENU_PYTEST_{uuid.uuid4()}',
            'description': f'NEW_DESCRIPTION_SUBMENU_PYTEST_{uuid.uuid4()}'
        }
        response = client.post(f'/{self.url}/{menu_id}/submenus/', json=data)
        assert response.status_code == 201
        assert response.json()['title'] == data['title']
        assert response.json()['description'] == data['description']
        assert 'dishes_count' in response.json() and (
            response.json()['dishes_count'] == 0
        )

    # Обновляет подменю
    def test_update_submenu(self, menu_id, submenu_id):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'

        updated_data = {
            'title': f'Updated Test SubMenu_{uuid.uuid4()}',
            'description': f'Updated Test SubMenu Description_{uuid.uuid4()}'
        }

        response = client.patch(f'/{self.url}/{menu_id}/submenus/{submenu_id}', json=updated_data)
        assert response.status_code == 200
        assert response.json()['title'] == updated_data['title']
        assert response.json()['description'] == updated_data['description']

        assert 'submenus_count' not in response.json()

        assert 'dishes_count' in response.json() and (
            response.json()['dishes_count'] == 0
        )

    # Удалить подменю
    def test_delete_submenu(self, menu_id, submenu_id):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'

        response = client.delete(f'/{self.url}/{menu_id}/submenus/{submenu_id}')
        assert response.status_code == 200

        response = client.get(f'/{self.url}/{menu_id}/submenus/{submenu_id}')
        assert response.status_code == 404, 'Ошибка 404'


class TestDish:
    base_url = 'http://localhost:8000'
    url = 'api/v1/menus'

    # Просмотр списка подменю
    def test_get_dish(self, menu_id, submenu_id):
        response = client.get(
            f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes'
        )
        assert response.status_code == 200
        assert response.json() == [], 'JSON-ответ не пустой, ожидался пустой список'

    # Создать блюдо
    def test_create_dish(self, menu_id, submenu_id):
        data = {
            'price': '9.99',
            'title': 'New Dish Title',
            'description': 'New Dish Description'
        }
        response = client.post(
            f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes', json=data
        )
        assert response.status_code == 201
        assert response.json()['price'] == data['price']
        assert response.json()['title'] == data['title']
        assert response.json()['description'] == data['description']

    # Обновить блюдо
    def test_update_dish(self, menu_id, submenu_id, dish_id):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        assert dish_id is not None, 'ID блюда не был сохранен'

        updated_data = {
            'price': '666',
            'title': f'Updated Test Dish_{uuid.uuid4()}',
            'description': f'Updated Test Dish Description_{uuid.uuid4()}'
        }

        response = client.patch(
            f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
            json=updated_data
        )
        assert response.status_code == 200
        assert response.json()['price'] == updated_data['price']
        assert response.json()['title'] == updated_data['title']
        assert response.json()['description'] == updated_data['description']

    # Удалить блюдо
    def test_delete_dish(self, menu_id, submenu_id, dish_id):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        assert dish_id is not None, 'ID блюда не был сохранен'

        response = client.delete(
            f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
        )
        assert response.status_code == 200

        response = client.get(
            f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
        )
        assert response.status_code == 404, 'Ошибка 404'
