"""
Celery application configuration.
Separated from FastAPI app to prevent circular imports.
"""

from celery import Celery
from config import get_settings

settings = get_settings()

celery = Celery(
    "cold_outreach",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuration
celery.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task routing
    task_default_queue="default",
    task_routes={
        "jobs.pipeline.*": {"queue": "pipeline"},
    },

    # Retry policy
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,

    # Result expiry (24 hours)
    result_expires=86400,

    # Auto-discover tasks in jobs/ package
    include=["jobs.pipeline"],
)
