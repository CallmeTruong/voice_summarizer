from worker.celery_app import celery_app
from infrastructure.vectors_controller import check_status
from infrastructure.obj_indices import bucket_parser, hash_generator
from core.retrieval import text2vect
from core.audio_process import check_status as upload_status
from infrastructure.vectors_controller import vectors
import boto3, os
from dotenv import load_dotenv
import time

load_dotenv()

dynamodb     = boto3.resource("dynamodb", os.getenv("REGION"))
status_table = dynamodb.Table(os.getenv("HISTORY_TABLE"))
raw_bucket_folder = os.getenv("RAW_BUCKET_FOLDER")


def _update_status(recording_id: str, status: str, progress: int, stage: str):
    status_table.update_item(
        Key={"raw_id": recording_id},
        UpdateExpression="SET #s = :s, progress = :p, stage = :st",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s":  status,
            ":p":  progress,
            ":st": stage,
        }
    )
    res = status_table.get_item(Key={"raw_id": recording_id})
    print(f"[DEBUG] get_item từ table: {status_table.table_name} | raw_id: {recording_id} | result: {res.get('Item')}")

@celery_app.task(bind=True, max_retries=3)
def process_audio_task(self, recording_id: str, transcript_id: str, file_name: str):
    try:
        item = status_table.get_item(Key={"raw_id": recording_id}).get("Item", {})
        if item.get("status") == "completed":
            print(f"[DEBUG] {recording_id} đã completed, skip")
            return

        _update_status(recording_id, "processing", 10, "uploading")

        print(f"[DEBUG] Checking S3 key: {raw_bucket_folder}/{recording_id}")
        result = upload_status.wait_until_uploaded(recording_id)
        print(f"[DEBUG] wait_until_uploaded returned: {result}")

        if not result:
            _update_status(recording_id, "failed", 0, "upload_not_found")
            return

        _update_status(recording_id, "processing", 30, "transcribing")
        time.sleep(15)

        check_status.wait_for_transcription(
            job_name=transcript_id,
            interval_seconds=10,
            timeout_seconds=36000
        )

        _update_status(recording_id, "processing", 70, "vectorizing")
        text2vect.vect_push(raw_id=recording_id, text_id=transcript_id)

        segments_data = vectors.get_segments(recording_id)
        summary_short = ""
        if segments_data:
            full_summary = segments_data.get("global_summary", "")
            summary_short = full_summary[:100] + "..." if len(full_summary) > 100 else full_summary

        result = status_table.update_item(
            Key={"raw_id": recording_id},
            UpdateExpression="SET #s = :s, progress = :p, stage = :st, text_id = :t, summaryShort = :ss",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s":  "completed",
                ":p":  100,
                ":st": "done",
                ":t":  transcript_id,
                ":ss": summary_short,
            }
        )
        print(f"[DEBUG] Final update result: {result.get('Attributes')}")

    except TimeoutError:
        _update_status(recording_id, "failed", 0, "timeout")

    except RuntimeError as exc:
        print(f"[ERROR] RuntimeError: {exc}")
        _update_status(recording_id, "failed", 0, "transcription_error")

    except Exception as exc:
        _update_status(recording_id, "failed", 0, "error")
        raise self.retry(exc=exc, countdown=60)
