from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "meeting_agent",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    imports=("app.services.task",),
    beat_schedule={
        "dispatch-reply-processing-every-1-minutes": {
            "task": "app.services.task.dispatch_reply_processing",
            "schedule": 60.0,
        },
        "cleanup-expired-tokens-every-1-hour": {
            "task": "app.services.task.cleanup_expired_tokens_task",
            "schedule": 3600.0,
        },
    },
)
