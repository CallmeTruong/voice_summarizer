from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
REDIS_BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/1")

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