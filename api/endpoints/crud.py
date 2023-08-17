from typing import Any, Dict
from uuid import UUID, uuid4

from fastapi import HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import exists
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from api.models.models import Dish, Menu, Submenu
from api.schemas.schemas import (DishesReturn, DishSchema, MenuSchema,
                                 SubmenuSchema)


@cache(expire=30)
async def get_menu_list(db) -> list[Menu]:
    """
    Получает список всех меню из базы данных.

    Параметры:
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        List[Menu]: Список объектов Menu.
    """

    menu = db.query(Menu).all()
    return menu


@cache(expire=30)
async def get_menu_by_id(menu_id: str, db: Session) -> Menu:
    """
    Получает определенное меню из базы данных по его идентификатору.

    Параметры:
        menu_id (str): Идентификатор меню.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        Menu: Объект Menu, соответствующий переданному идентификатору.

    Ошибки/исключения:
        HTTPException: Если меню с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
    """

    current_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if current_menu is None:
        raise HTTPException(status_code=404, detail='menu not found')
    return current_menu


@cache()
async def create_menu_func(menu: MenuSchema, db: Session) -> Menu:
    """
    Создает новое меню в базе данных.

    Параметры:
        menu (MenuSchema): Объект схемы данных MenuSchema
        с информацией о новом меню.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        Menu: Объект Menu, представляющий созданное меню.

    Ошибки/исключения:
        HTTPException: Если меню с таким же заголовком уже существует,
        возвращает код статуса 400 (Bad Request).
    """

    if db.query(exists().where(Menu.title == menu.title)).scalar():
        raise HTTPException(
            status_code=400, detail='Menu with this title already exists'
        )

    created_menu = Menu(
        id=uuid4(),
        title=menu.title,
        description=menu.description
    )
    db.add(created_menu)
    db.commit()
    db.refresh(created_menu)
    return created_menu


@cache()
async def put_menu(
    menu_id: str,
    menu: MenuSchema,
    db: Session
) -> Menu:
    """
    Обновляет информацию о существующем меню в базе данных.

    Параметры:
        - menu_id (str): Идентификатор меню, которое нужно обновить.
        - menu (MenuSchema): Объект схемы данных MenuSchema
        с обновленной информацией о меню.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Menu: Обновленный объект Menu.

    Ошибки/исключения:
        - HTTPException: Если меню с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
        - HTTPException: Если переданы пустые данные для обновления,
        возвращает код статуса 400 (Bad Request).
        - HTTPException: Если возникла ошибка при выполнении операции
        обновления в базе данных, возвращает код статуса 500.
    """

    menu_to_update = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu_to_update is None:
        raise HTTPException(status_code=404, detail='menu not found')
    menu_to_update.title = menu.title
    menu_to_update.description = menu.description
    db.add(menu_to_update)
    db.commit()
    db.refresh(menu_to_update)
    return menu_to_update


@cache()
async def delete_menu(menu_id: str, db: Session) -> Dict[str, Any]:
    """
    Удаляет меню из базы данных.

    Параметры:
        - menu_id (str): Идентификатор меню, которое нужно удалить.
        - db (Session): Сессия базы данных SQLAlchemy.

    Ошибки/исключения:
        - HTTPException: Если меню с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
    """

    menu_to_delete = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu_to_delete is None:
        raise HTTPException(status_code=404, detail='menu not found')
    db.delete(menu_to_delete)
    db.commit()


@cache(expire=30)
async def get_list_submenu(
    api_test_menu_id: UUID,
    db: Session
) -> list[Submenu]:
    """
    Получает список всех подменю определенного меню из базы данных.

    Параметры:
        - api_test_menu_id (UUID): Идентификатор меню.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращат:
        - List[Submenu]: Список объектов Submenu,
        соответствующих переданному идентификатору меню.
    """

    api_test_menu_id_str = str(api_test_menu_id)
    submenus = db.query(Submenu).filter(
        Submenu.menu_id == api_test_menu_id_str).all()
    return submenus


@cache(expire=30)
async def get_submenu_by_id(
    api_test_submenu_id: str | None,
    db: Session
) -> Submenu:
    """
    Получает определенное подменю из базы данных по его идентификатору.

    Параметры:
        - api_test_submenu_id (str | None): Идентификатор подменю.
        Может быть None, если передана строка 'null'.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Submenu: Объект Submenu, соответствующий переданному идентификатору.

    Ошибки/исключения:
        - HTTPException: Если подменю с указанным идентификатором
        не найдено, возвращает код статуса 404 (Not Found).
    """

    if api_test_submenu_id == 'null':
        api_test_submenu_id = None

    current_submenu = db.query(Submenu).filter(
        Submenu.id == api_test_submenu_id).first()

    if current_submenu is None:
        raise HTTPException(status_code=404, detail='submenu not found')

    return current_submenu


@cache()
async def create_submenu_func(
    target_menu_id: str,
    submenu: SubmenuSchema,
    db: Session
) -> Submenu:
    """
    Создает новое подменю в базе данных.

    Параметры:
        - target_menu_id (str): Идентификатор меню, к которому
        относится новое подменю.
        - submenu (SubmenuSchema): Объект схемы данных SubmenuSchema
        с информацией о новом подменю.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Submenu: Объект Submenu, представляющий созданное подменю.

    Ошибки/исключения:
        - HTTPException: Если меню с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
    """

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


@cache()
async def put_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: Session
) -> Submenu:
    """
    Обновляет информацию о существующем подменю в базе данных.

    Параметры:
        - api_test_menu_id (str): Идентификатор меню,
        к которому относится подменю.
        - api_test_submenu_id (str): Идентификатор подменю,
        которое нужно обновить.
        - submenu_update (SubmenuSchema): Объект схемы данных SubmenuSchema
        с обновленной информацией о подменю.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Submenu: Обновленный объект Submenu.

    Ошибки/исключения:
        - HTTPException: Если подменю с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
        - HTTPException: Если переданы пустые данные для обновления,
        возвращает код статуса 400 (Bad Request).
        - HTTPException: Если возникла ошибка при выполнении операции
        обновления в базе данных, возвращает код статуса 500.
    """

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


@cache()
async def delete_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Удаляет подменю из базы данных.

    Параметры:
        - api_test_menu_id (str): Идентификатор меню,
        к которому относится подменю.
        - api_test_submenu_id (str): Идентификатор подменю,
        которое нужно удалить.
        - db (Session): Сессия базы данных SQLAlchemy.

    Ошибки/исключения:
        - HTTPException: Если подменю с указанными идентификаторами не найдено,
        возвращает код статуса 404 (Not Found).
    """

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


@cache(expire=30)
async def get_list_dish(submenu_id: UUID, db: Session) -> list[Dish]:
    """
    Получает список всех блюд определенного подменю из базы данных.

    Параметры:
        submenu_id (UUID): Идентификатор подменю.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        List[Dish]: Список объектов Dish,
        соответствующих переданному идентификатору подменю.
    """

    submenu_id_str = str(submenu_id)
    current_dishes = db.query(Dish).filter(
        Dish.submenu_id == submenu_id_str).all()
    dishes_list = [DishesReturn.from_orm(dish) for dish in current_dishes]
    return dishes_list


@cache(expire=30)
async def get_dish_by_id(dish_id: str, db: Session) -> Dish:
    """
    Получает определенное блюдо из базы данных по его идентификатору.

    Параметры:
        - dish_id (str): Идентификатор блюда.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Dish: Объект Dish, соответствующий переданному идентификатору.

    Ошибки/исключения:
        - HTTPException: Если блюдо с указанным идентификатором не найдено,
        возвращает код статуса 404 (Not Found).
    """

    current_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if current_dish is None:
        raise HTTPException(status_code=404, detail='dish not found')
    return current_dish


@cache()
async def create_dish_func(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    dish: DishSchema,
    db: Session
) -> Dish:
    """
    Создает новое блюдо в базе данных.

    Параметры:
        - api_test_menu_id (str): Идентификатор меню,
        к которому относится подменю.
        - api_test_submenu_id (str): Идентификатор подменю,
        к которому относится блюдо.
        - dish (DishSchema): Объект схемы данных DishSchema
        с информацией о новом блюде.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Dish: Объект Dish, представляющий созданное блюдо.

    Ошибки/исключения:
        - HTTPException: Если меню или подменю с указанными идентификаторами
        не найдены, возвращает код статуса 404 (Not Found).
    """

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


@cache()
async def put_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    dish_update: DishSchema,
    db: Session
) -> Dish:
    """
    Обновляет информацию о существующем блюде в базе данных.

    Параметры:
        - api_test_menu_id (str): Идентификатор меню,
        к которому относится подменю.
        - api_test_submenu_id (str): Идентификатор подменю,
        к которому относится блюдо.
        - api_test_dish_id (str): Идентификатор блюда,
        которое нужно обновить.
        - dish_update (DishSchema): Объект схемы данных DishSchema
        с обновленной информацией о блюде.
        - db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        - Dish: Обновленный объект Dish.

    Ошибки/исключения:
        - HTTPException: Если блюдо с указанными идентификаторами
        не найдено, возвращает код статуса 404 (Not Found).
        - HTTPException: Если переданы пустые данные для обновления,
        возвращает код статуса 400 (Bad Request).
        - HTTPException: Если возникла ошибка при выполнении операции
        обновления в базе данных, возвращает код статуса 500.
    """

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


@cache()
async def delete_dish(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    api_test_dish_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Удаляет блюдо из базы данных.

    Параметры:
        - api_test_menu_id (str): Идентификатор меню,
        к которому относится подменю.
        - api_test_submenu_id (str): Идентификатор подменю,
        к которому относится блюдо.
        - api_test_dish_id (str): Идентификатор блюда,
        которое нужно удалить.
        - db (Session): Сессия базы данных SQLAlchemy.

    Ошибки/исключения:
        - HTTPException: Если блюдо с указанными идентификаторами
        не найдено, возвращает код статуса 404 (Not Found).
    """

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
