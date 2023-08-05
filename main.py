import redis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.endpoints.router import router as router_operation

app = FastAPI(title='YP Project')

app.include_router(router_operation)


try:
    redis_host = 'redis'
    redis_port = 6379
    redis_db = 0

    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    pong = redis_client.ping()
    if pong:
        print('Подключение к Redis успешно!')
    else:
        print('Не удалось подключиться к Redis.')
except redis.ConnectionError as e:
    print(f'Ошибка подключения к Redis: {e}')


cache_backend = RedisBackend(redis_client)
FastAPICache.init(cache_backend, prefix='fastapi-cache')
