
import uuid

import httpx
import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import Redis

from api.config.config import BASE_URL, REDIS_DB, REDIS_HOST, REDIS_PORT, URL
from api.data.database import get_db
from main import app

client = TestClient(app)


@pytest.fixture(scope='class')
async def http_client():
    async with httpx.AsyncClient(
        app=app,
        base_url=BASE_URL
    ) as client:
        yield client


@pytest.fixture(scope='function')
async def clear_cache():
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    cache_backend = RedisBackend(redis)
    FastAPICache.init(cache_backend, prefix='fastapi-cache')
    await cache_backend.clear()


@pytest.fixture(autouse=True)
async def before_and_after_test(clear_cache, db=get_db()):
    yield
    try:
        db.rollback()
    except Exception as e:
        print("Error rolling back transaction:", e)
    await clear_cache()


@pytest.fixture(scope='function')
async def menu_id():
    data = {
        'title': f'NEW_TITLE_MENU_PYTEST_{uuid.uuid4()}',
        'description': f'NEW_DESCRIPTION_MENU_PYTEST_{uuid.uuid4()}'
    }
    async for client in http_client:
        response = await client.post('/api/v1/menus', json=data)
        assert response.status_code == 201
        return response.json()['id']


@pytest.fixture(scope='function')
async def submenu_id(menu_id):
    data = {
        'title': f'NEW_TITLE_SUBMENU_PYTEST_{uuid.uuid4()}',
        'description': f'NEW_DESCRIPTION_SUBMENU_PYTEST_{uuid.uuid4()}'
    }
    async for client in http_client:
        response = await client.post(
            f'/api/v1/menus/{menu_id}/submenus/',
            json=data
        )
        assert response.status_code == 201
        return response.json()['id']


@pytest.fixture(scope='function')
async def dish_id(menu_id, submenu_id):
    data = {
        'price': f'3.99_{uuid.uuid4()}',
        'title': f'New Dish Title2_{uuid.uuid4()}',
        'description': f'New Dish Description2_{uuid.uuid4()}'
    }
    async for client in http_client:
        response = await client.post(
            f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=data
        )
        assert response.status_code == 201
        assert response.json()['price'] == data['price']
        assert response.json()['title'] == data['title']
        assert response.json()['description'] == data['description']
        return response.json()['id']


class TestMenu:
    base_url = BASE_URL
    url = URL

    # Просматривает список меню
    @pytest.mark.order(1)
    @pytest.mark.asyncio
    async def test_get_list_menu(self, http_client):
        async for client in http_client:
            response = await client.get(f'/{self.url}')
            assert response.status_code == 200
            assert (
                response.json() == []
            ), 'JSON-ответ не пустой, ожидался пустой список'

    # Создает меню
    @pytest.mark.order(2)
    @pytest.mark.asyncio
    async def test_async_create_menu(self, http_client):
        data = {
            'title': f'NEW_TITLE_MENU_PYTEST_{uuid.uuid4()}',
            'description': f'NEW_DESCRIPTION_MENU_PYTEST_{uuid.uuid4()}'
        }

        async for client in http_client:
            response = await client.post(f'/{self.url}', json=data)

            assert response.status_code == 201
            assert response.json()['title'] == data['title']
            assert response.json()['description'] == data['description']
            assert 'submenus_count' in response.json() and (
                response.json()['submenus_count'] == 0
            )
            assert 'dishes_count' in response.json() and (
                response.json()['dishes_count'] == 0
            )

    # Просматривает список подменю
    @pytest.mark.order(3)
    @pytest.mark.asyncio
    async def test_get_list_submenu(self, menu_id, http_client):
        async for client in http_client:
            response = await client.get(f'/{self.url}/{menu_id}/submenus')
            assert response.status_code == 200
            assert (
                response.json() == []
            ), 'JSON-ответ не пустой, ожидался пустой список'

    # Создать подменю
    @pytest.mark.order(4)
    @pytest.mark.asyncio
    async def test_create_submenu(self, menu_id, http_client):
        data = {
            'title': f'NEW_TITLE_SUBMENU_PYTEST_{uuid.uuid4()}',
            'description': f'NEW_DESCRIPTION_SUBMENU_PYTEST_{uuid.uuid4()}'
        }
        async for client in http_client:
            response = await client.post(
                f'/{self.url}/{menu_id}/submenus',
                json=data
            )
            assert response.status_code == 201
            assert response.json()['title'] == data['title']
            assert response.json()['description'] == data['description']
            assert 'dishes_count' in response.json() and (
                response.json()['dishes_count'] == 0
            )

    # Просматривает список блюд
    @pytest.mark.order(5)
    @pytest.mark.asyncio
    async def test_get_list_dish(self, menu_id, submenu_id, http_client):
        async for client in http_client:
            response = await client.get(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes'
            )
            assert response.status_code == 200
            assert (
                response.json() == []
            ), 'JSON-ответ не пустой, ожидался пустой список'

    # Создать блюдо
    @pytest.mark.order(6)
    @pytest.mark.asyncio
    async def test_create_dish(self, menu_id, submenu_id, http_client):
        data = {
            'price': f'9._{uuid.uuid4()}',
            'title': f'New Dish Title_{uuid.uuid4()}',
            'description': f'New Dish Description_{uuid.uuid4()}'
        }
        async for client in http_client:
            response = await client.post(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes',
                json=data
            )
            assert response.status_code == 201
            assert response.json()['price'] == data['price']
            assert response.json()['title'] == data['title']
            assert response.json()['description'] == data['description']

    # Обновляет меню
    @pytest.mark.order(7)
    @pytest.mark.asyncio
    async def test_update_current_menu(self, menu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'

        updated_data = {
            'title': f'Updated Test Menu_{uuid.uuid4()}',
            'description': f'Updated Test Menu Description_{uuid.uuid4()}'
        }
        async for client in http_client:
            response = await client.patch(
                f'/{self.url}/{menu_id}',
                json=updated_data
            )
            assert response.status_code == 200
            assert response.json()['title'] == updated_data['title']
            assert (
                response.json()['description'] == updated_data['description']
            )
            assert 'submenus_count' in response.json() and (
                response.json()['submenus_count'] == 0
            )
            assert 'dishes_count' in response.json() and (
                response.json()['dishes_count'] == 0
            )

    # Обновляет подменю
    @pytest.mark.order(8)
    @pytest.mark.asyncio
    async def test_update_submenu(self, menu_id, submenu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'

        updated_data = {
            'title': f'Updated Test SubMenu_{uuid.uuid4()}',
            'description': f'Updated Test SubMenu Description_{uuid.uuid4()}'
        }
        async for client in http_client:
            response = await client.patch(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}',
                json=updated_data
            )
            assert response.status_code == 200
            assert response.json()['title'] == updated_data['title']
            assert (
                response.json()['description'] == updated_data['description']
            )

            assert 'submenus_count' not in response.json()

            assert 'dishes_count' in response.json() and (
                response.json()['dishes_count'] == 0
            )

    # Обновить блюдо
    @pytest.mark.order(9)
    @pytest.mark.asyncio
    async def test_update_dish(
        self,
        menu_id,
        submenu_id,
        dish_id,
        http_client
    ):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        assert dish_id is not None, 'ID блюда не был сохранен'

        updated_data = {
            'price': '666',
            'title': f'Updated Test Dish_{uuid.uuid4()}',
            'description': f'Updated Test Dish Description_{uuid.uuid4()}'
        }
        async for client in http_client:
            response = await client.patch(
                f'/{self.url}/{menu_id}/submenus/'
                f'{submenu_id}/dishes/{dish_id}',
                json=updated_data
            )
            assert response.status_code == 200
            assert response.json()['price'] == updated_data['price']
            assert response.json()['title'] == updated_data['title']
            assert (
                response.json()['description'] == updated_data['description']
            )

    # Просматривает определенное меню
    @pytest.mark.order(10)
    @pytest.mark.asyncio
    async def test_get_target_menu(self, menu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'
        async for client in http_client:
            response = await client.get(f'/{self.url}/{menu_id}')

            assert response.status_code == 200
            assert response.json()['id'] == menu_id

    # Просматривает список меню
    @pytest.mark.order(11)
    @pytest.mark.asyncio
    async def test_get_list_menu_not_empty(self, http_client):
        async for client in http_client:
            response = await client.get(f'/{self.url}')
            assert response.status_code == 200
            assert (
                response.json() != []
            ), 'JSON-ответ пустой, ожидался непустой список'

    # Просматривает определенное подменю
    @pytest.mark.order(12)
    @pytest.mark.asyncio
    async def test_get_target_submenu(self, menu_id, submenu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        async for client in http_client:
            response = await client.get(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}'
            )

            assert response.status_code == 200
            assert response.json()['id'] == submenu_id
            assert response.json()['menu_id'] == menu_id

    # Просматривает список подменю
    @pytest.mark.order(13)
    @pytest.mark.asyncio
    async def test_get_list_submenu_not_empty(self, menu_id, http_client):
        async for client in http_client:
            response = await client.get(f'/{self.url}/{menu_id}/submenus')
            assert response.status_code == 200
            assert (
                response.json() == []
            ), 'JSON-ответ не пустой, ожидался пустой список'

    # Просматривает определенное блюдо
    @pytest.mark.order(14)
    @pytest.mark.asyncio
    async def test_get_target_d(
        self,
        menu_id,
        submenu_id,
        dish_id,
        http_client
    ):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        assert dish_id is not None, 'ID блюда не был сохранен'
        async for client in http_client:
            response = await client.get(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
            )

            assert response.status_code == 200
            assert response.json()['id'] == dish_id
            assert response.json()['submenu_id'] == submenu_id

    # Удалить блюдо
    @pytest.mark.order(15)
    @pytest.mark.asyncio
    async def test_delete_dish(
        self,
        menu_id,
        submenu_id,
        dish_id,
        http_client
    ):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        assert dish_id is not None, 'ID блюда не был сохранен'

        async for client in http_client:
            response = await client.delete(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
            )
            assert response.status_code == 200

        async for client in http_client:
            response = await client.get(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
            )
            assert response.status_code == 404, 'Ошибка 404'

    # Удалить подменю
    @pytest.mark.order(16)
    @pytest.mark.asyncio
    async def test_delete_submenu(self, menu_id, submenu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'
        assert submenu_id is not None, 'ID подменю не был сохранен'
        async for client in http_client:
            response = await client.delete(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}'
            )
            assert response.status_code == 200
        async for client in http_client:
            response = await client.get(
                f'/{self.url}/{menu_id}/submenus/{submenu_id}'
            )
            assert response.status_code == 404, 'Ошибка 404'

    # Удаляет созданное меню
    @pytest.mark.order(17)
    @pytest.mark.asyncio
    async def test_delete_menu(self, menu_id, http_client):
        assert menu_id is not None, 'ID меню не был сохранен'
        async for client in http_client:
            response = await client.delete(f'/{self.url}/{menu_id}')
            assert response.status_code == 200
        async for client in http_client:
            response = await client.get(f'/{self.url}/{menu_id}')
            assert response.status_code == 404, 'Ошибка 404'
