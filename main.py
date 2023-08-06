import os

import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.endpoints.router import router as router_operation

load_dotenv()
app = FastAPI(title='YP Project')

app.include_router(router_operation)

redis_host: str = os.environ.get('REDIS_HOST', 'redis')
redis_port: int = int(os.environ.get('REDIS_PORT', 6379))
redis_db: int = int(os.environ.get('REDIS_DB', 0))

try:
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
