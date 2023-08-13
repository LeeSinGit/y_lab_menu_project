from cachetools import TTLCache

# Создаем кэш
cache: TTLCache[str, None] = TTLCache(maxsize=100, ttl=30)


def background_invalidate_menu_list() -> None:
    cache.pop('menu_list', None)


def background_invalidate_submenu_list() -> None:
    cache.pop('submenu_list', None)


def background_invalidate_dish_list() -> None:
    cache.pop('dish_list', None)
