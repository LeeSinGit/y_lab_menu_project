from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from api.data.database import get_db
from api.endpoints.crud import (create_dish_func, create_menu_func,
                                create_submenu_func, delete_dish, delete_menu,
                                delete_submenu, get_dish_by_id, get_list_dish,
                                get_list_submenu, get_menu_by_id,
                                get_menu_list, get_submenu_by_id, put_dish,
                                put_menu, put_submenu)
from api.models import models
from api.schemas.schemas import (CreateDish, CreateMenu, CreateSubMenu,
                                 DishesReturn, DishesWithID, DishSchema,
                                 MenuSchema, MenuSchemaWithID, SubmenuSchema,
                                 SubmenuSchema2, SubmenuSchemaWithID,
                                 UpdateDishes, UpdateMenu, UpdateSubmenu)

router = APIRouter(prefix='/api/v1', tags=['CRUD'])


@router.get(
    '/menus',
    response_model=list[MenuSchema],
    summary='Получить список меню',
    response_description='Список всех меню'
)
async def get_list_menu(db: Session = Depends(get_db)) -> list[models.Menu]:
    menu = await get_menu_list(db)
    return menu


@router.get(
    '/menus/{menu_id}',
    response_model=MenuSchemaWithID,
    summary='Получить меню по id',
    response_description=(
        'Получить меню по его'
        'уникальному идентификатору (id)'
    )
)
async def get_target_menu(
    menu_id: str,
    db: Session = Depends(get_db)
) -> models.Menu:
    current_menu = await get_menu_by_id(menu_id, db)
    return current_menu


# Создать меню
@router.post(
    '/menus',
    response_model=CreateMenu,
    status_code=status.HTTP_201_CREATED,
    summary='Создать меню',
    response_description='Создать новое меню'
)
async def create_menu(
    menu: MenuSchema,
    db: Session = Depends(get_db)
) -> models.Menu:
    created_menu = await create_menu_func(menu, db)
    return created_menu


# Обновить меню
@router.patch(
    '/menus/{menu_id}',
    response_model=UpdateMenu,
    summary='Обновить меню',
    response_description='Обновить уже имеющееся в базе данных меню'
)
async def update_current_menu(
    menu_id: str,
    menu: MenuSchema,
    db: Session = Depends(get_db)
) -> models.Menu:
    menu_to_update = await put_menu(menu_id, menu, db)
    return menu_to_update


# Удалить меню
@router.delete(
    '/menus/{menu_id}',
    summary='Удалить меню',
    response_description='Удалить уже имеющееся в базе данных меню'
)
async def delete_current_menu(
    menu_id: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    await delete_menu(menu_id, db)


# Просмотр списка подменю
@router.get(
    '/menus/{api_test_menu_id}/submenus',
    response_model=list[SubmenuSchema2],
    status_code=status.HTTP_200_OK,
    summary='Получить список подменю',
    response_description='Получить список всех подменю'
)
async def all_submenus(
    api_test_menu_id: UUID4,
    db: Session = Depends(get_db)
) -> list[models.Submenu]:
    submenus = await get_list_submenu(api_test_menu_id, db)
    return submenus


# Просмотр определенного подменю
@router.get(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}',
    response_model=SubmenuSchemaWithID,
    summary='Получить определённое подменю',
    response_description=(
        'Получить подменю,'
        'привязанное к определённому меню по id'
    )
)
async def get_target_submenu(
    api_test_submenu_id: UUID4,
    db: Session = Depends(get_db)
) -> models.Submenu:
    current_submenu = await get_submenu_by_id(api_test_submenu_id, db)
    return current_submenu


# Создать подменю
@router.post(
    '/menus/{target_menu_id}/submenus',
    response_model=CreateSubMenu,
    status_code=status.HTTP_201_CREATED,
    summary='Создать подменю',
    response_description=(
        'Создать подменю,'
        'привязанное к определённому меню по id'
    )
)
async def create_submenu(
    target_menu_id: str,
    submenu: SubmenuSchema,
    db: Session = Depends(get_db)
) -> models.Submenu:
    current_menu = await create_submenu_func(target_menu_id, submenu, db)
    return current_menu


# Обновить подменю
@router.patch(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}',
    response_model=UpdateSubmenu,
    summary='Обновить подменю',
    response_description=(
        'Обновить подменю,'
        'уже имеющееся в базе данных'
    )
)
async def update_current_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: Session = Depends(get_db)
) -> models.Submenu:
    current_submenu = await put_submenu(
        api_test_menu_id,
        api_test_submenu_id,
        submenu_update,
        db
    )
    return current_submenu


# Удалить подменю
@router.delete(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}',
    summary='Удалить подменю',
    response_description='Удалить подменю'
)
async def delete_current_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    await delete_submenu(api_test_menu_id, api_test_submenu_id, db)


# Просмотр списка блюд
@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[DishesReturn],
    status_code=status.HTTP_200_OK,
    summary='Получить список блюд',
    response_description='Список блюд для конкретного подменю (по id)'
)
async def get_dishes(
    submenu_id: UUID,
    db: Session = Depends(get_db)
) -> models.Dish:
    dishes_list = await get_list_dish(submenu_id, db)
    return dishes_list


# Посмотреть определённое блюдо
@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishesWithID,
    summary='Получить определённое блюдо',
    response_description=(
        'Получить блюдо для конкретного'
        'подменю (по id), связанного с меню (по id)'
    )
)
async def receive_current_dish(
    dish_id: str,
    db: Session = Depends(get_db)
) -> models.Dish:
    current_dish = await get_dish_by_id(dish_id, db)
    return current_dish


# Создать блюдо
@router.post(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes',
    response_model=CreateDish,
    status_code=status.HTTP_201_CREATED,
    summary='Создать определённое блюдо',
    response_description=(
        'Создать блюдо для конкретного'
        'подменю (по id), связанного с меню (по id)'
    )
)
async def create_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    dish: DishSchema,
    db: Session = Depends(get_db)
) -> models.Dish:
    current_dish = await create_dish_func(
        api_test_menu_id,
        api_test_submenu_id,
        dish,
        db
    )
    return current_dish


# Обновить блюдо
@router.patch(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/'
    'dishes/{api_test_dish_id}',
    response_model=UpdateDishes,
    summary='Обновить определённое блюдо',
    response_description=(
        'Обновить блюдо для конкретного'
        'подменю (по id), связанного с меню (по id)'
    )
)
async def update_current_menu_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    dish_update: DishSchema,
    db: Session = Depends(get_db)
) -> models.Dish:
    dish_to_update = await put_dish(
        api_test_menu_id,
        api_test_submenu_id,
        api_test_dish_id,
        dish_update,
        db
    )
    return dish_to_update


# Удалить блюдо
@router.delete(
    '/menus/{api_test_menu_id}/submenus/'
    '{api_test_submenu_id}/dishes/{api_test_dish_id}',
    summary='Удалить блюдо',
    response_description='Удалить определённое блюдо'
)
async def delete_current_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    await delete_dish(
        api_test_menu_id,
        api_test_submenu_id,
        api_test_dish_id,
        db
    )
