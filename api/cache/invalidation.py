from cachetools import TTLCache

# Создаем кэш
cache = TTLCache(maxsize=100, ttl=30)


def background_invalidate_menu_list():
    cache.pop('menu_list', None)


def background_invalidate_submenu_list():
    cache.pop('submenu_list', None)


def background_invalidate_dish_list():
    cache.pop('dish_list', None)
