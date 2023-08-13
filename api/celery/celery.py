from celery import Celery

from api.config.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

# Создаем экземпляр объекта Celery
celery = Celery(
    'tasks',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//'
)

celery.autodiscover_tasks(['api.celery2'])
