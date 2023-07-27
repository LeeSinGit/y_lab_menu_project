from uuid import UUID, uuid4

from fastapi import HTTPException
from models.models import Dish, Menu, Submenu
from pydantic import UUID4
from schemas.schemas import DishesReturn, DishSchema, MenuSchema, SubmenuSchema
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound


# Просмотр списка меню
async def get_menu_list(db):
    menu = db.query(Menu).all()
    return menu


# Просмотр определенного меню
async def get_menu_by_id(menu_id: str, db: Session):
    current_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='menu not found')
    return current_menu


# Создать меню
async def create_menu_func(menu: MenuSchema, db: Session):
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
async def put_menu(
    menu_id: str,
    menu: MenuSchema,
    db: Session
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
async def delete_menu(menu_id: str, db: Session):
    menu_to_delete = db.query(Menu).filter(Menu.id == menu_id).first()
    db.delete(menu_to_delete)
    db.commit()


# Просмотр списка подменю
async def get_list_submenu(api_test_menu_id: UUID, db: Session):
    api_test_menu_id_str = str(api_test_menu_id)
    submenus = db.query(Submenu).filter(
        Submenu.menu_id == api_test_menu_id_str).all()
    return submenus


# Просмотр определенного подменю
async def get_submenu_by_id(api_test_submenu_id: str, db: Session):
    if api_test_submenu_id == 'null':
        api_test_submenu_id = None

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id).first()

    if current_submenu is None:
        raise HTTPException(status_code=404, detail='submenu not found')

    return current_submenu


# Создать подменю
async def create_submenu_func(
    target_menu_id: str,
    submenu: SubmenuSchema,
    db: Session
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
async def put_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: Session
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
async def delete_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: Session
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
async def get_list_dish(submenu_id: UUID, db: Session):
    submenu_id_str = str(submenu_id)
    current_dishes = db.query(Dish).filter(
        Dish.submenu_id == submenu_id_str).all()
    dishes_list = [DishesReturn.from_orm(dish) for dish in current_dishes]
    return dishes_list


# Просмотреть определённое блюдо
async def get_dish_by_id(dish_id: str, db: Session):
    current_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if current_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return current_dish


# Создать блюдо
async def create_dish_func(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    dish: DishSchema,
    db: Session
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
async def put_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    dish_update: DishSchema,
    db: Session
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
async def delete_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    db: Session
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
