from celery import Celery

from app.core.config import settings

celery_app = Celery("vulnscope", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="vulnscope.placeholder")
def placeholder_task() -> str:
    return "ready"
# Project version: VulnScope V1.5



