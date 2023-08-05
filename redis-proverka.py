import redis


# Создаем клиент Redis
redis_client = redis.StrictRedis(host='redis_cache', port=6379, db=0)

# Проверяем доступность сервера Redis
try:
    response = redis_client.ping()
    if response:
        print("Сервер Redis доступен.")
    else:
        print("Сервер Redis не отвечает.")
except redis.exceptions.ConnectionError:
    print("Не удалось подключиться к серверу Redis.")
