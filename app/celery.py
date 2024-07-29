import nest_asyncio
import asyncio
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.core.tasks import notification_task

nest_asyncio.apply()

broker_use_ssl = {
    "ssl_cert_reqs": "CERT_NONE",
}

celery = Celery(
    "tasks",
    broker=f"rediss://{settings.redis.host}:{settings.redis.port}/0",
    broker_use_ssl=broker_use_ssl,
)


@celery.task
def send_notifications():
    asyncio.run(notification_task())


celery.conf.beat_schedule = {
    "run-task": {
        "task": "app.celery.send_notifications",
        "schedule": crontab(hour="0", minute="0"),
    },
}

celery.conf.broker_connection_retry_on_startup = True
