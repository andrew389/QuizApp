import nest_asyncio
import asyncio

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.tasks import notification_task

nest_asyncio.apply()

celery = Celery("tasks", broker=settings.redis.url)


@celery.task
def send_notifications():
    asyncio.run(notification_task())


celery.conf.beat_schedule = {
    "run-task": {
        "task": "app.celery.send_notifications",
        "schedule": crontab(minute="*"),
    },
}

celery.conf.broker_connection_retry_on_startup = True
