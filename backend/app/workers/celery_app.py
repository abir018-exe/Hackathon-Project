from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "last_mile_stabilizer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.scanner",
        "app.workers.tasks.intelligence",
        "app.workers.tasks.stabilization",
        "app.workers.tasks.testing",
        "app.workers.tasks.demo_script",
        "app.workers.tasks.risk",
    ],
)

celery_app.conf.update(
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.workers.tasks"])