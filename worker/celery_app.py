from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_BROKER_URL = os.getenv("CELERY_BROKER_URL")
REDIS_BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND")

if not REDIS_BROKER_URL or not REDIS_BACKEND_URL:
    raise RuntimeError(
        "CELERY_BROKER_URL and CELERY_RESULT_BACKEND must be configured."
    )

celery_app = Celery(
    "voice_summarizer",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=False,
    task_track_started=True,
)
