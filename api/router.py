from typing import List
from uuid import UUID, uuid4

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Dish, Menu, Submenu
from pydantic import UUID4
from schemas import (
    DishesReturn,
    DishSchema,
    MenuSchema,
    SubmenuSchema,
    SubmenuSchema2,
)
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound


router = APIRouter(prefix='/api/v1', tags=['CRUD'])


# Просмотр списка меню
@router.get('/menus', response_model=List[MenuSchema])
async def get_list_menu(db: Session = Depends(get_db)):
    menu = db.query(Menu).all()
    return menu


# Просмотр определенного меню
@router.get('/menus/{menu_id}')
async def get_target_menu(menu_id: str, db: Session = Depends(get_db)):
    current_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='menu not found')
    return current_menu


# Создать меню
@router.post('/menus', status_code=status.HTTP_201_CREATED)
async def create_menu(menu: MenuSchema, db: Session = Depends(get_db)):
    created_menu = Menu(
        id=uuid4(),
        title=menu.title,
        description=menu.description
    )
    db.add(created_menu)
    db.commit()
    db.refresh(created_menu)
    return created_menu


# Обновить меню
@router.patch('/menus/{menu_id}')
async def update_current_menu(
    menu_id: str,
    menu: MenuSchema,
    db: Session = Depends(get_db)
):
    menu_to_update = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu_to_update is None:
        raise HTTPException(status_code=404, detail='menu not found')
    menu_to_update.title = menu.title
    menu_to_update.description = menu.description
    db.add(menu_to_update)
    db.commit()
    db.refresh(menu_to_update)
    return menu_to_update


# Удалить меню
@router.delete('/menus/{menu_id}')
async def delete_current_menu(menu_id: str, db: Session = Depends(get_db)):
    menu_to_delete = db.query(Menu).filter(Menu.id == menu_id).first()
    db.delete(menu_to_delete)
    db.commit()


# Просмотр списка подменю
@router.get(
        '/menus/{api_test_menu_id}/submenus',
        response_model=List[SubmenuSchema2],
        status_code=status.HTTP_200_OK
)
async def all_submenus(api_test_menu_id: UUID4, db: Session = Depends(get_db)):
    submenus = db.query(Submenu).filter(
        Submenu.menu_id == api_test_menu_id).all()
    return submenus


# Просмотр определенного подменю
@router.get('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def get_target_submenu(
    api_test_submenu_id: str,
    db: Session = Depends(get_db)
):

    if api_test_submenu_id == 'null':
        api_test_submenu_id = None

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id).first()

    if current_submenu is None:
        raise HTTPException(status_code=404, detail='submenu not found')

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
    current_menu = db.query(Menu).filter(Menu.id == target_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')
    db_submenu = Submenu(
        id=uuid4(),
        title=submenu.title,
        description=submenu.description,
        menu_id=target_menu_id
    )

    current_menu.add_submenu_count(1)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


# Обновить подменю
@router.patch('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def update_current_menu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: Session = Depends(get_db)
):
    if not submenu_update.dict():
        raise HTTPException(
            status_code=400,
            detail='No data provided for update'
        )

    current_menu = db.query(Menu).filter(Menu.id == api_test_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')

    submenu_to_update = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id,
        Submenu.menu_id == api_test_menu_id).first()
    if submenu_to_update is None:
        raise HTTPException(status_code=404, detail='Submenu not found')

    for key, value in submenu_update.dict().items():
        setattr(submenu_to_update, key, value)

    try:
        db.commit()
        db.refresh(submenu_to_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail='Failed to update submenu. Error: ' + str(e)
        )
    return submenu_to_update


# Удалить подменю
@router.delete('/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}')
async def delete_current_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: Session = Depends(get_db)
):
    current_menu = db.query(Menu).filter(Menu.id == api_test_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')

    try:
        submenu_to_delete = db.query(Submenu).filter(
            Submenu.id == api_test_submenu_id).first()

        dish_count = submenu_to_delete.dishes_count
        current_menu.delete_submenu_count(1)
        current_menu.delete_dishes_count(dish_count)
        db.delete(submenu_to_delete)
        db.commit()
        return submenu_to_delete
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Submenu not found')


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
    current_dishes = db.query(Dish).filter(Dish.submenu_id == submenu_id).all()
    dishes_list = [DishesReturn.from_orm(dish) for dish in current_dishes]
    return dishes_list


# Посмотреть определённое блюдо
@router.get('/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def receive_current_dish(dish_id: str, db: Session = Depends(get_db)):
    current_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if current_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
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
    current_menu = db.query(Menu).filter(Menu.id == api_test_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id).first()
    if current_submenu is None:
        raise HTTPException(status_code=404, detail='Submenu not found')
    current_menu.add_dishes_count(1)
    current_submenu.update_dishes_count(1)

    db_dish = Dish(
        id=uuid4(),
        title=dish.title,
        description=dish.description,
        price=dish.price,
        submenu_id=api_test_submenu_id)

    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


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
    if not dish_update.dict():
        raise HTTPException(
            status_code=400,
            detail='No data provided for update'
        )

    current_menu = db.query(Menu).filter(Menu.id == api_test_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id,
        Submenu.menu_id == api_test_menu_id).first()
    if current_submenu is None:
        raise HTTPException(status_code=404, detail='Submenu not found')

    dish_to_update = db.query(Dish).filter(
        Dish.id == api_test_dish_id,
        Dish.submenu_id == api_test_submenu_id).first()

    for key, value in dish_update.dict().items():
        setattr(dish_to_update, key, value)

    try:
        db.commit()
        db.refresh(dish_to_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail='Failed to update dish. Error: ' + str(e)
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

    current_menu = db.query(Menu).filter(Menu.id == api_test_menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='Menu not found')

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id,
        Submenu.menu_id == api_test_menu_id).first()
    if current_submenu is None:
        raise HTTPException(status_code=404, detail='Submenu not found')

    try:
        current_menu.delete_dishes_count(1)
        dish_to_delete = db.query(Dish).filter(
            Dish.id == api_test_dish_id,
            Dish.submenu_id == api_test_submenu_id).one()
        db.delete(dish_to_delete)
        db.commit()
        return dish_to_delete
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Dish not found')
