from typing import List
from uuid import UUID

from crud import (
    create_dish_func,
    create_menu_func,
    create_submenu_func,
    delete_dish,
    delete_menu,
    delete_submenu,
    get_dish_by_id,
    get_list_dish,
    get_list_submenu,
    get_menu_by_id,
    get_menu_list,
    get_submenu_by_id,
    put_dish,
    put_menu,
    put_submenu,
)
from database import get_db
from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from schemas import (
    DishesReturn,
    DishSchema,
    MenuSchema,
    SubmenuSchema,
    SubmenuSchema2,
)
from sqlalchemy.orm import Session


router = APIRouter(prefix='/api/v1', tags=['CRUD'])


# Просмотр списка меню
@router.get('/menus', response_model=List[MenuSchema])
async def get_list_menu(db: Session = Depends(get_db)):
    menu = await get_menu_list(db)
    return menu


# Просмотр определенного меню
@router.get('/menus/{menu_id}')
async def get_target_menu(menu_id: str, db: Session = Depends(get_db)):
    current_menu = await get_menu_by_id(menu_id, db)
    return current_menu


# Создать меню
@router.post('/menus', status_code=status.HTTP_201_CREATED)
async def create_menu(menu: MenuSchema, db: Session = Depends(get_db)):
    created_menu = await create_menu_func(menu, db)
    return created_menu


# Обновить меню
@router.patch('/menus/{menu_id}')
async def update_current_menu(
    menu_id: str,
    menu: MenuSchema,
    db: Session = Depends(get_db)
):
    menu_to_update = await put_menu(menu_id, menu, db)
    return menu_to_update


# Удалить меню
@router.delete('/menus/{menu_id}')
async def delete_current_menu(menu_id: str, db: Session = Depends(get_db)):
    await delete_menu(menu_id, db)


# Просмотр списка подменю
@router.get(
    '/menus/{api_test_menu_id}/submenus',
    response_model=List[SubmenuSchema2],
    status_code=status.HTTP_200_OK
)
async def all_submenus(api_test_menu_id: UUID4, db: Session = Depends(get_db)):
    submenus = await get_list_submenu(api_test_menu_id, db)
    return submenus


# Просмотр определенного подменю
@router.get('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def get_target_submenu(
    api_test_submenu_id: str,
    db: Session = Depends(get_db)
):
    current_submenu = await get_submenu_by_id(api_test_submenu_id, db)
    return current_submenu


# Создать подменю
@router.post(
    '/menus/{target_menu_id}/submenus',
    status_code=status.HTTP_201_CREATED
)
async def create_submenu(
    target_menu_id: str,
    submenu: SubmenuSchema,
    db: Session = Depends(get_db)
):
    current_menu = await create_submenu_func(target_menu_id, submenu, db)
    return current_menu


# Обновить подменю
@router.patch('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def update_current_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: Session = Depends(get_db)
):
    current_submenu = await put_submenu(
        api_test_menu_id,
        api_test_submenu_id,
        submenu_update,
        db
    )

    return current_submenu


# Удалить подменю
@router.delete('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def delete_current_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: Session = Depends(get_db)
):
    await delete_submenu(api_test_menu_id, api_test_submenu_id, db)


# Просмотр списка блюд
@router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[DishesReturn],
    status_code=status.HTTP_200_OK,
    summary='Список блюд для конкретного подменю (по идентификатору подменю)',
    responses={
        404: {'description': 'меню не найдено'},
    },
)
async def get_dishes(submenu_id: UUID, db: Session = Depends(get_db)):
    dishes_list = await get_list_dish(submenu_id, db)
    return dishes_list


# Посмотреть определённое блюдо
@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def receive_current_dish(dish_id: str, db: Session = Depends(get_db)):
    current_dish = await get_dish_by_id(dish_id, db)
    return current_dish


# Создать блюдо
@router.post(
    '/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes',
    status_code=status.HTTP_201_CREATED
)
async def create_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    dish: DishSchema,
    db: Session = Depends(get_db)
):
    current_dish = await create_dish_func(
        api_test_menu_id,
        api_test_submenu_id,
        dish,
        db
    )
    return current_dish


# Обновить блюдо
@router.patch(('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/'
               'dishes/{api_test_dish_id}'))
async def update_current_menu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    dish_update: DishSchema,
    db: Session = Depends(get_db)
):
    dish_to_update = await put_dish(
        api_test_menu_id,
        api_test_submenu_id,
        api_test_dish_id,
        dish_update,
        db
    )
    return dish_to_update


# Удалить блюдо
@router.delete('/menus/{api_test_menu_id}/submenus/'
               '{api_test_submenu_id}/dishes/{api_test_dish_id}')
async def delete_current_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    db: Session = Depends(get_db)
):

    await delete_dish(
        api_test_menu_id,
        api_test_submenu_id,
        api_test_dish_id,
        db
    )
