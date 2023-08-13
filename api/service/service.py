from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.models.models import Dish, Menu, Submenu


# Получить меню или ошибку 404
async def get_menu_or_404(menu_id: str, db: AsyncSession) -> Menu:
    stmt = select(Menu).where(Menu.id == menu_id)
    result = await db.execute(stmt)
    current_menu = result.scalar()

    if current_menu is None:
        raise HTTPException(status_code=404, detail='menu not found')

    return current_menu


# Получить подменю или ошибку 404
async def get_submenu_or_404(
    api_test_submenu_id: str | None,
    db: AsyncSession
) -> Submenu:

    if api_test_submenu_id == 'null':
        api_test_submenu_id = None

    stmt = select(Submenu).where(Submenu.id == api_test_submenu_id)
    result = await db.execute(stmt)
    current_submenu = result.scalar()

    if current_submenu is None:
        raise HTTPException(status_code=404, detail='submenu not found')

    return current_submenu


# Получить блюдо или ошибку 404
async def get_dish_or_404(dish_id: str, db: AsyncSession) -> Dish:

    current_dish = select(Dish).where(
        Dish.id == dish_id)
    result = await db.execute(current_dish)
    current_dish = result.scalar()

    if current_dish is None:
        raise HTTPException(status_code=404, detail='dish not found')

    return current_dish
