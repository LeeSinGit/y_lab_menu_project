from uuid import UUID, uuid4

from fastapi import BackgroundTasks, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from api.cache.invalidation import (
    background_invalidate_dish_list,
    background_invalidate_menu_list,
    background_invalidate_submenu_list,
)
from api.celery2.tasks import send_menu_created_email
from api.models.models import Dish, Menu, Submenu
from api.schemas.schemas import (
    DishesWithID,
    DishSchema,
    MenuSchema,
    MenuSchemaWithID,
    SubmenuSchema,
    SubmenuSchemaWithID,
)
from api.service.service import get_dish_or_404, get_menu_or_404, get_submenu_or_404

background_tasks = BackgroundTasks()


@cache(expire=30)
async def get_menu_list(db: AsyncSession) -> list[Menu]:
    """
    Получить список меню из базы данных.
    Параметры:
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - list[Menu]: Список объектов меню.
    """

    stmt = select(Menu)
    result = await db.execute(stmt)
    menu = result.scalars().all()
    return menu


@cache(expire=30)
async def get_menu_by_id(menu_id: str, db: AsyncSession) -> Menu:
    """
    Получить объект меню по его идентификатору.
    Параметры:
    - menu_id: str - Идентификатор меню.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Menu: Объект меню.
    """

    return await get_menu_or_404(menu_id, db)


@cache()
async def create_menu_func(menu: MenuSchema, db: AsyncSession) -> Menu:
    """
    Создать новое меню и добавить его в базу данных.
    Параметры:
    - menu: MenuSchema - Схема данных нового меню.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Menu: Созданный объект меню.
    """

    async with db.begin():
        new_menu = Menu(
            id=uuid4(),
            title=menu.title,
            description=menu.description,
        )
        db.add(new_menu)
        await db.commit()

    send_menu_created_email.delay(menu.title, menu.description)
    background_tasks.add_task(background_invalidate_menu_list)
    return MenuSchemaWithID(**menu.dict(), id=new_menu.id)


@cache()
async def put_menu(
    menu_id: str,
    menu: MenuSchema,
    db: AsyncSession
) -> Menu:
    """
    Обновить информацию о существующем меню.
    Параметры:
    - menu_id: str - Идентификатор меню, которое нужно обновить.
    - menu: MenuSchema - Схема данных для обновления меню.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Menu: Обновленный объект меню.
    """

    async with db.begin():
        current_menu = await get_menu_or_404(menu_id, db)
        if current_menu:
            current_menu.title = menu.title
            current_menu.description = menu.description
            await db.commit()
            background_tasks.add_task(background_invalidate_menu_list)
            return current_menu
        else:
            raise HTTPException(status_code=404, detail='menu not found')


@cache()
async def delete_menu(menu_id: str, db: AsyncSession):
    """
    Удалить меню из базы данных.
    Параметры:
    - menu_id: str - Идентификатор меню для удаления.
    - db: AsyncSession - Асинхронная сессия базы данных.
    - В случае успешного удаления меню, ничего не возвращает.
    - В случае, если меню с заданным
    идентификатором не найдено,
    генерирует исключение HTTPException с кодом 404.
    """

    async with db.begin():
        menu_to_delete = await db.get(Menu, menu_id)
        if menu_to_delete:
            await db.delete(menu_to_delete)
            await db.commit()
            background_tasks.add_task(background_invalidate_menu_list)
        else:
            raise HTTPException(status_code=404, detail='menu not found')


@cache(expire=30)
async def get_list_submenu(
    api_test_menu_id: UUID,
    db: AsyncSession
) -> list[Submenu]:
    """
    Получить список подменю для заданного меню.
    Параметры:
    - api_test_menu_id: UUID - Идентификатор меню,
    для которого нужно получить список подменю.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - list[Submenu]: Список объектов подменю.
    """

    api_test_menu_id_str = str(api_test_menu_id)
    stmt = select(Submenu).where(Submenu.menu_id == api_test_menu_id_str)
    result = await db.execute(stmt)
    submenu = result.scalars().all()
    return submenu


@cache(expire=30)
async def get_submenu_by_id(
    api_test_submenu_id: str | None,
    db: AsyncSession
) -> Submenu:
    """
    Получить подменю по его идентификатору.
    Параметры:
    - api_test_submenu_id: str | None - Идентификатор подменю,
    которое нужно получить.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Submenu: Объект подменю.
    """

    return await get_submenu_or_404(api_test_submenu_id, db)


@cache()
async def create_submenu_func(
    target_menu_id: str,
    submenu: SubmenuSchema,
    db: AsyncSession
) -> Submenu:
    """
    Создать новое подменю и добавить его в базу данных.
    Параметры:
    - target_menu_id: str - Идентификатор меню,
    к которому будет привязано подменю.
    - submenu: SubmenuSchema - Схема данных нового подменю.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Submenu: Созданный объект подменю.
    """

    async with db.begin():
        current_menu = await get_menu_or_404(target_menu_id, db)

        db_submenu = Submenu(
            id=uuid4(),
            title=submenu.title,
            description=submenu.description,
            menu_id=target_menu_id
        )
        current_menu.add_submenu_count(1)
        db.add(db_submenu)
        await db.commit()

    background_tasks.add_task(background_invalidate_submenu_list)

    return SubmenuSchemaWithID(
        **submenu.dict(),
        id=db_submenu.id,
        menu_id=target_menu_id
    )


@cache()
async def put_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    submenu_update: SubmenuSchema,
    db: AsyncSession
) -> Submenu:
    """
    Обновить информацию о существующем подменю.
    Параметры:
    - api_test_menu_id: str - Идентификатор меню,
    к которому принадлежит подменю.
    - api_test_submenu_id: str - Идентификатор подменю, которое нужно обновить.
    - submenu_update: SubmenuSchema - Схема данных для обновления подменю.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Submenu: Обновленный объект подменю.
    """

    if not submenu_update.dict():
        raise HTTPException(
            status_code=400,
            detail='No data provided for update'
        )
    async with db.begin():
        current_submenu_to_update = await get_submenu_or_404(
            api_test_submenu_id,
            db
        )

        await db.execute(update(Submenu).where(
            Submenu.id == api_test_submenu_id
        ).values(**submenu_update.dict()))

        await db.commit()

    await db.refresh(current_submenu_to_update)

    background_tasks.add_task(background_invalidate_submenu_list)

    return current_submenu_to_update


@cache()
async def delete_submenu(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    db: AsyncSession
):
    """
    Удалить подменю из базы данных.
    Параметры:
    - api_test_menu_id: str - Идентификатор меню,
    к которому принадлежит подменю.
    - api_test_submenu_id: str - Идентификатор подменю для удаления.
    - db: AsyncSession - Асинхронная сессия базы данных.
    - В случае успешного удаления подменю, ничего не возвращает.
    - В случае, если подменю с
    заданным идентификатором не найдено,
    генерирует исключение HTTPException с кодом 404.
    """

    async with db.begin():
        current_menu = await get_menu_or_404(api_test_menu_id, db)

        try:
            current_submenu_to_delete = await get_submenu_or_404(
                api_test_submenu_id,
                db
            )

            dish_count = current_submenu_to_delete.dishes_count
            current_menu.delete_submenu_count(1)
            current_menu.delete_dishes_count(dish_count)
            await db.delete(current_submenu_to_delete)
            await db.commit()

            background_tasks.add_task(background_invalidate_submenu_list)

            return current_submenu_to_delete
        except NoResultFound:
            raise HTTPException(status_code=404, detail='Submenu not found')


@cache(expire=30)
async def get_list_dish(submenu_id: UUID, db: AsyncSession) -> list[Dish]:
    """
    Получить список блюд для заданного подменю.
    Параметры:
    - submenu_id: UUID - Идентификатор подменю,
    для которого нужно получить список блюд.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - list[Dish]: Список объектов блюд.
    """

    submenu_id_str = str(submenu_id)
    current_dishes = select(Dish).where(
        Dish.submenu_id == submenu_id_str)
    result = await db.execute(current_dishes)
    dishes_list = result.scalars().all()
    return dishes_list


@cache(expire=30)
async def get_dish_by_id(dish_id: str, db: AsyncSession) -> Dish:
    """
    Получить блюдо по его идентификатору.
    Параметры:
    - dish_id: str - Идентификатор блюда, которое нужно получить.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Dish: Объект блюда.
    """

    return await get_dish_or_404(dish_id, db)


@cache()
async def create_dish_func(
    api_test_menu_id: str,
    api_test_submenu_id: str,
    dish: DishSchema,
    db: AsyncSession
) -> Dish:
    """
    Создать новое блюдо и добавить его в базу данных.
    Параметры:
    - api_test_menu_id: str - Идентификатор меню,
    к которому принадлежит подменю.
    - api_test_submenu_id: str - Идентификатор подменю,
    к которому будет привязано блюдо.
    - dish: DishSchema - Схема данных нового блюда.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Dish: Созданный объект блюда.
    """

    async with db.begin():

        current_menu = await get_menu_or_404(api_test_menu_id, db)
        current_submenu = await get_submenu_or_404(
            api_test_submenu_id,
            db
        )

        current_menu.add_dishes_count(1)
        current_submenu.update_dishes_count(1)

        db_dish = Dish(
            id=uuid4(),
            title=dish.title,
            description=dish.description,
            price=dish.price,
            submenu_id=api_test_submenu_id)

        db.add(db_dish)
        await db.commit()

        background_tasks.add_task(background_invalidate_dish_list)

        return DishesWithID(
            **dish.dict(),
            id=db_dish.id,
            submenu_id=api_test_submenu_id
        )


@cache()
async def put_dish(
    api_test_submenu_id: str,
    api_test_dish_id: str,
    dish_update: DishSchema,
    db: AsyncSession
) -> Dish:
    """
    Обновить информацию о существующем блюде.
    Параметры:
    - api_test_menu_id: str - Идентификатор меню,
    к которому принадлежит подменю.
    - api_test_submenu_id: str - Идентификатор подменю,
    к которому принадлежит блюдо.
    - api_test_dish_id: str - Идентификатор блюда, которое нужно обновить.
    - dish_update: DishSchema - Схема данных для обновления блюда.
    - db: AsyncSession - Асинхронная сессия базы данных.
    Возвращает:
    - Dish: Обновленный объект блюда.
    """

    if not dish_update.dict():
        raise HTTPException(
            status_code=400,
            detail='No data provided for update'
        )
    async with db.begin():
        current_dish_to_update = await get_dish_or_404(api_test_dish_id, db)

        await db.execute(
            update(Dish)
            .where(
                Dish.id == api_test_dish_id,
                Dish.submenu_id == api_test_submenu_id
            )
            .values(**dish_update.dict())
        )

        await db.commit()

    await db.refresh(current_dish_to_update)

    background_tasks.add_task(background_invalidate_dish_list)

    return current_dish_to_update


@cache()
async def delete_dish(
    api_test_submenu_id: str,
    api_test_dish_id: str,
    db: Session
):
    """
    Удалить блюдо из базы данных.
    Параметры:
    - api_test_menu_id: str - Идентификатор меню,
    к которому принадлежит подменю.
    - api_test_submenu_id: str - Идентификатор подменю,
    к которому принадлежит блюдо.
    - api_test_dish_id: str - Идентификатор блюда для удаления.
    - db: Session - Сессия базы данных.
    - В случае успешного удаления блюда, ничего не возвращает.
    - В случае, если блюдо с
    заданным идентификатором не найдено,
    генерирует исключение HTTPException с кодом 404.
    """

    async with db.begin():
        current_menu = await get_menu_or_404(api_test_submenu_id, db)

        try:
            current_menu.delete_dishes_count(1)
            current_dish_to_delete = await get_dish_or_404(
                api_test_dish_id,
                db
            )

            await db.delete(current_dish_to_delete)
            await db.commit()

            background_tasks.add_task(background_invalidate_dish_list)

            return current_dish_to_delete
        except NoResultFound:
            raise HTTPException(status_code=404, detail='Dish not found')


# Получить все объекты
@cache(expire=30)
async def get_all_menus_with_submenus_and_dishes_func(db: AsyncSession):
    stmt = select(Menu)
    result = await db.execute(stmt)
    menu = result.scalars().all()

    stmt = select(Submenu)
    result = await db.execute(stmt)
    submenu = result.scalars().all()

    current_dishes = select(Dish)
    result = await db.execute(current_dishes)
    dishes_list = result.scalars().all()

    return menu, submenu, dishes_list
