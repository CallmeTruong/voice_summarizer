# worker/celery_app.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv(".env")

celery_app = Celery(
    "voice_summarizer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    task_track_started=True,
)