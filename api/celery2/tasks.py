import asyncio
from uuid import UUID

import httpx
import pandas as pd
from pandas.core.series import Series

from api.celery.celery import celery
from api.celery.send_email import send_email
from api.config.config import BASE_URL, URL
from api.main import app


@celery.task
def send_menu_created_email(menu_title, menu_description):
    subject = 'Новое меню создано'
    message = (
        f'Создано новое меню:\nНазвание:'
        f'{menu_title}\nОписание: {menu_description}'
    )
    to_email = 'semen.lisin2019@yandex.ru'
    send_email(subject, message, to_email)


async def process_menu_row(row: Series, app_url: str) -> dict:
    """Обрабатывает CRUD-операции для строки меню в Excel"""

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        menu_id = row.iloc[0]
        title = row.iloc[1]
        description = row.iloc[2]

        data = {
            'id': menu_id,
            'title': title,
            'description': description,
        }
        keys = set(data.keys())

        response = await client.get(
            f'http://api:8000/api/v1/menus/{menu_id}'
        )
        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                'http://api:8000/api/v1/menus', json=data
            )
            print(f'Меню создано:\n{result.json()}')

        elif response.status_code == 200 and all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return data

        else:
            result = await client.patch(
                app.url_path_for('update_current_menu', menu_id=menu_id), json=data
            )
            print('Меню обновлено!')

        return result.json()


async def process_submenu_row(row: Series, menu_id: UUID) -> dict:
    """Обрабатывает CRUD-операции для строки подменю в Excel"""

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        submenu_id = row.iloc[1]
        title = row.iloc[2]
        description = row.iloc[3]

        data = {
            'id': submenu_id,
            'title': title,
            'description': description,
        }
        keys = set(data.keys())

        response = await client.get(
            f'http://api:8000/api/v1/menus/{menu_id}/submenus/{submenu_id}'
        )

        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                f'http://api:8000/api/v1/menus/{menu_id}/submenus', json=data
            )
            print(f'Подменю создано:\n{result.json()}')

        elif response.status_code == 200 and all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return data

        else:
            result = await client.patch(
                app.url_path_for(
                    'update_current_submenu', submenu_id=submenu_id, menu_id=menu_id
                ),
                json=data,
            )
            print('Подменю обновлено!')

        return result.json()


async def process_dish_row(row: Series, menu_id: UUID, submenu_id: UUID):
    """Обрабатывает CRUD-операции для строки блюда в Excel"""

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        dish_id = row.iloc[2]
        title = row.iloc[3]
        description = row.iloc[4]
        price = str(row.iloc[5])

        data = {
            'id': dish_id,
            'title': title,
            'description': description,
            'price': price,
        }
        keys = set(data.keys())

        response = await client.get(
            f'http://api:8000/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
        )

        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                f'http://api:8000/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=data
            )
            print(f'Блюдо создано:\n{result.json()}')

        elif response.status_code == 200 and all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return None

        else:
            result = await client.patch(
                f'http://api:8000/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                json=data,
            )
            print('Блюдо обновлено!')

        return result.json()


async def track_xlsx_to_db(app_url: str) -> None:
    """
    Функция для отслеживания файла XLSX и
    преобразования таблиц в базу данных
    """

    menu_list: list[dict] = []
    menu_counter: int = -1
    submenu_counter: int = 0

    menu_df = pd.read_excel('api/admin/Menu.xlsx', header=None)

    for index, row in menu_df.iterrows():

        if pd.notnull(row.iloc[0]):
            submenu_counter = -1
            menu = await process_menu_row(row, app_url)
            menu['submenus'] = []
            menu_list.append(menu)
            menu_counter += 1

        elif row.iloc[1:4].notna().all():
            submenu = await process_submenu_row(
                row, menu_list[menu_counter]['id']
            )
            submenu['dishes'] = []
            menu_list[menu_counter]['submenus'].append(submenu)
            submenu_counter += 1

        elif row.iloc[2:6].notna().all():
            current_menu = menu_list[menu_counter]
            current_submenu = current_menu['submenus'][submenu_counter]
            dish = await process_dish_row(
                row,
                menu_id=current_menu['id'],
                submenu_id=current_submenu['id']
            )
            (menu_list[menu_counter]['submenus']
             [submenu_counter]['dishes'].append(dish))


@celery.task
def run_xlsx_tracking():
    """Запускает отслеживание в цикле событий"""

    loop = asyncio.get_event_loop()
    app_url = f'/{URL}'
    try:
        result = loop.run_until_complete(track_xlsx_to_db(app_url))
        if result is None:
            print('Обновлений нет')
        return result
    except Exception as e:
        print(f'An error occurred: {e}')
        raise
