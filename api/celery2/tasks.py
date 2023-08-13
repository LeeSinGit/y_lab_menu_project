import asyncio
from uuid import UUID

import httpx
import pandas as pd
from pandas.core.series import Series

from api.celery.celery import celery
from api.celery.send_email import send_email
from api.config.config import BASE_URL
from api.main import app


@celery.task
def send_menu_created_email(menu_title, menu_description):
    subject = "Новое меню создано"
    message = (
        f'Создано новое меню:\nНазвание:'
        f'{menu_title}\nОписание: {menu_description}'
    )
    to_email = 'semen.lisin2019@yandex.ru'
    send_email(subject, message, to_email)


async def process_menu_row(row: Series) -> dict:
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

        response = await client.get(app.url_path_for(
            'read_menu', menu_id=menu_id)
        )
        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                app.url_path_for('create_menu'), json=data
            )
            print(f'Меню создано:\n{result.json()}')

        elif all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return data

        else:
            result = await client.patch(
                app.url_path_for('patch_menu', menu_id=menu_id), json=data
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
            app.url_path_for(
                'read_submenu', submenu_id=submenu_id, menu_id=menu_id
            )
        )

        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                app.url_path_for('create_submenu', menu_id=menu_id), json=data
            )
            print(f'Подменю создано:\n{result.json()}')

        elif all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return data

        else:
            result = await client.patch(
                app.url_path_for(
                    'update_submenu', submenu_id=submenu_id, menu_id=menu_id
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
            app.url_path_for(
                'read_dish',
                submenu_id=submenu_id,
                menu_id=menu_id,
                dish_id=dish_id
            )
        )

        response_json = response.json()

        if response.status_code == 404:
            result = await client.post(
                app.url_path_for(
                    'create_dish',
                    menu_id=menu_id,
                    submenu_id=submenu_id
                ),
                json=data,
            )
            print(f'Блюдо создано:\n{result.json()}')

        elif all(response_json[key] == data[key] for key in keys):
            print('Нет изменений для обновления')
            return data

        else:
            result = await client.patch(
                app.url_path_for(
                    'patch_dish',
                    submenu_id=submenu_id,
                    menu_id=menu_id,
                    dish_id=dish_id,
                ),
                json=data,
            )
            print('Блюдо обновлено!')

        return result.json()


async def cleanup_database(menu_list: list[dict]) -> None:
    """Очищает базу данных в случае удаления записей из таблицы Excel"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        response_menus = await client.get(app.url_path_for('read_menus'))
        response_menus_json = response_menus.json()

        await cleanup_menu(response_menus_json, menu_list, client)

        await cleanup_submenu(menu_list, client)


async def cleanup_menu(
    response_menus_json: dict, menu_list: list[dict], client: httpx.AsyncClient
) -> None:
    """Удаляет меню, отсутствующие в таблице Excel"""

    if len(response_menus_json) > len(menu_list):
        menu_xlsx_id_list: list[UUID] = [menu['id'] for menu in menu_list]
        menu_db_id_list: list[UUID] = (
            [menu['id'] for menu in response_menus_json]
        )

        non_matches = list(set(menu_db_id_list).difference(menu_xlsx_id_list))

        if non_matches:
            for menu_id in non_matches:
                await client.delete(
                    app.url_path_for('delete_menu', menu_id=menu_id)
                )


async def cleanup_submenu(
        menu_list: list[dict],
        client: httpx.AsyncClient
) -> None:
    """Удаляет подменю, отсутствующие в таблице Excel"""

    submenu_xlsx_id_list: list[dict[str, UUID]] = []
    submenu_db_id_list: list[dict[str, UUID]] = []

    for menu in menu_list:
        response_submenus = await client.get(
            app.url_path_for('read_submenus', menu_id=menu['id'])
        )
        response_submenus_json = response_submenus.json()

        submenu_list = menu['submenus']
        await cleanup_dishes(submenu_list, menu['id'], client)

        if len(response_submenus_json) > len(menu['submenus']):
            submenu_xlsx_id_list += [
                {'submenu_id': submenu['id'], 'menu_id': menu['id']}
                for submenu in menu['submenus']
            ]
            submenu_db_id_list += [
                {'submenu_id': submenu['id'], 'menu_id': submenu['menu_id']}
                for submenu in response_submenus_json
            ]

    non_matches: list[dict] = list(
        set(submenu_db_id_list).difference(submenu_xlsx_id_list)
    )

    if non_matches:
        for submenu in non_matches:
            await client.delete(
                app.url_path_for(
                    'delete_submenu',
                    menu_id=submenu['menu_id'],
                    submenu_id=submenu['submenu_id'],
                )
            )


async def cleanup_dishes(
    submenu_list: list[dict], menu_id: UUID, client: httpx.AsyncClient
) -> None:
    """Удаляет блюда, отсутствующие в таблице Excel"""

    dish_xlsx_id_list: list[tuple] = []
    dish_db_id_list: list[tuple] = []

    for submenu in submenu_list:
        response_dishes = await client.get(
            app.url_path_for(
                'read_dishes',
                menu_id=menu_id,
                submenu_id=submenu['id'],
            ),
            params={'filter_by_submenu': True},
        )

        response_dishes_json = response_dishes.json()

        if len(response_dishes_json) > len(submenu['dishes']):
            dish_xlsx_id_list += [
                (
                    dish['id'],
                    submenu['id'],
                    menu_id,
                )
                for dish in submenu['dishes']
            ]
            dish_db_id_list += [
                (
                    dish['id'],
                    submenu['id'],
                    menu_id,
                )
                for dish in response_dishes_json
            ]

    non_matches: list[tuple] = (
        list(set(dish_db_id_list).difference(dish_xlsx_id_list))
    )

    if non_matches:
        for dish in non_matches:
            await client.delete(
                app.url_path_for(
                    'delete_dish',
                    dish_id=dish[0],
                    submenu_id=dish[1],
                    menu_id=dish[2],
                )
            )


async def track_xlsx_to_db() -> None:
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
            menu = await process_menu_row(row)
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

    await cleanup_database(menu_list)


@celery.task
def run_xlsx_tracking():
    """Запускает отслеживание в цикле событий"""

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(track_xlsx_to_db())
