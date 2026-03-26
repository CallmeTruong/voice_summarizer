from worker.celery_app import celery_app
from infrastructure.vectors_controller import check_status
from infrastructure.obj_indices import bucket_parser, hash_generator
from core.retrieval import audio2text, text2vect
from core.audio_process import check_status as upload_status
import boto3, os
from dotenv import load_dotenv
import time


bucket            = os.getenv("BUCKET_NAME")
client            = os.getenv("CLIENT")
raw_bucket_folder = os.getenv("RAW_BUCKET_FOLDER")
table             = os.getenv("TABLE_NAME")

load_dotenv(".env")

dynamodb     = boto3.resource("dynamodb", os.getenv("REGION"))
status_table = dynamodb.Table(os.getenv("HISTORY_TABLE"))


def _update_status(recording_id: str, status: str, progress: int, stage: str):
    status_table.update_item(
        Key={"raw_id": recording_id},
        UpdateExpression="SET #s = :s, progress = :p, stage = :st",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": status,
            ":p": progress,
            ":st": stage,
        }
    )


@celery_app.task(bind=True, max_retries=3)
def process_audio_task(self, recording_id: str, transcript_id :str, file_name: str):
    
    try:

        # upload lên S3
        _update_status(recording_id, "processing", 10, "uploading")
        
        # Thêm print để xem key đang check
        print(f"[DEBUG] Checking S3 key: raw_audio/{recording_id}")
        
        result = upload_status.wait_until_uploaded(recording_id)
        print(f"[DEBUG] wait_until_uploaded returned: {result}")
        
        if not result:
            _update_status(recording_id, "failed", 0, "upload_not_found")
            return



        raw_id  = recording_id
        text_id = transcript_id

        #chờ Lambda + Transcribe xong
        _update_status(recording_id, "processing", 30, "transcribing")

        time.sleep(15)

        check_status.wait_for_transcription(
            job_name=text_id,
            interval_seconds=10,
            timeout_seconds=36000
        )

        #lấy transcript từ S3 → push vector
        _update_status(recording_id, "processing", 70, "vectorizing")

        text2vect.vect_push(raw_id=raw_id, text_id=text_id)

        # Lưu raw_id thật để assistant query dùng
        _update_status(recording_id, "completed", 100, "done")
        status_table.update_item(
            Key={"raw_id": recording_id},
            UpdateExpression="SET actual_raw_id = :r, actual_text_id = :t",
            ExpressionAttributeValues={
                ":r": raw_id,
                ":t": text_id,
            }
        )

    except TimeoutError:
        _update_status(recording_id, "failed", 0, "timeout")

    except Exception as exc:
        _update_status(recording_id, "failed", 0, "error")
        raise self.retry(exc=exc, countdown=60)