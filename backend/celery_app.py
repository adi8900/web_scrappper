from celery import Celery
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")

celery = Celery(
    "scraper",
    broker=f"redis://{REDIS_HOST}:6379/0",
    backend=f"redis://{REDIS_HOST}:6379/0"
)

import tasks
