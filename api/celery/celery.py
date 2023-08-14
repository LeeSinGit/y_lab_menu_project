from celery import Celery

from api.config.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

# Создаем экземпляр объекта Celery
celery = Celery(
    'tasks',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//'
)

celery.autodiscover_tasks(['api.celery2'])


celery.conf.beat_schedule = {
    'run-xlsx-tracking': {
        'task': 'api.celery2.tasks.run_xlsx_tracking',
        'schedule': 15.0,
    },
}
