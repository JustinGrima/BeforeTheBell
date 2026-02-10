from celery import Celery

from app.core.config import settings

celery_app = Celery("beforethebell", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "daily-summary": {
        "task": "app.tasks.jobs.send_daily_reports",
        "schedule": 60.0,
    }
}
