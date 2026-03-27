# api/routers/recordings.py
from fastapi import APIRouter, HTTPException
from api.schemas.request import (
    QueryRequest, UploadUrlRequest,
    ProcessRequest, UpdateRecordingRequest
)
from core.model_controller import memory as mem_module
from worker.tasks import process_audio_task
import boto3, os, uuid
from infrastructure.obj_indices import bucket_parser, hash_generator
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
from datetime import datetime, timezone
import json

load_dotenv(".env")
router = APIRouter(prefix="/api/recordings")

dynamodb     = boto3.resource("dynamodb", os.getenv("REGION"))
status_table = dynamodb.Table(os.getenv("HISTORY_TABLE"))
s3           = boto3.client("s3", region_name=os.getenv("REGION"))
BUCKET       = os.getenv("BUCKET_NAME")
path = os.getenv("RAW_BUCKET_FOLDER")
table = os.getenv("TABLE_NAME")
user_table = dynamodb.Table(os.getenv("USER_TABLE"))


@router.post("/upload-url")
async def get_upload_url(user_id: str, request: UploadUrlRequest):
    recording_id = hash_generator.hash_key()
    s3_key = f"{path}/{recording_id}"
    transcript_obj = hash_generator.hash_key()

    mapper = bucket_parser.HashTable(
        size=16,
        bucket=BUCKET, 
        key=f"{table}.json"
    )
    mapper.insert(recording_id, transcript_obj)

    upload_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket":      BUCKET,
            "Key":         s3_key,
            "ContentType": request.contentType,
        },
        ExpiresIn=900
    )

    # Lưu vào DynamoDB để tracking
    status_table.put_item(Item={
        "raw_id":   recording_id,
        "text_id":   transcript_obj,
        "status":   "pending",
        "progress": 0,
        "stage":    "waiting",
        "fileName": request.fileName,
        "file_type": request.contentType,
        "durationSec": request.durationSec,
        "s3_key":   s3_key,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })
    print(f"[DEBUG] put_item vào table: {status_table.table_name} | raw_id: {recording_id}")

    user_table.put_item(Item={
        "user_id": user_id,
        "raw_id":   recording_id,
    })

    print(f"[DEBUG] put_item vào table: {user_table.table_name} | user_id: {user_id}")

    return {
        "success": True,
        "data": {
            "recordingId": recording_id,
            "transcriptId": transcript_obj,
            "uploadUrl":   upload_url,
            "fileUrl":     f"https://{BUCKET}.s3.amazonaws.com/{s3_key}",
            "expiresIn":   900
        }
    }


@router.get("/{recording_id}")
async def get_recording(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": f"{recording_id} không tồn tại"
        })

    # Tạo presigned URL
    audio_url = None
    if item.get("s3_key"):
        try:
            audio_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET, "Key": item["s3_key"]},
                ExpiresIn=3600
            )
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "id":           recording_id,
            "title":        item.get("title", item.get("fileName", "")),
            "fileName":     item.get("fileName", ""),
            "status":       item.get("status", "unknown"),
            "createdAt":    item.get("createdAt", ""),
            "durationSec":  item.get("durationSec", None),
            "audioUrl":     audio_url,
            "summaryShort": item.get("summaryShort", ""),
        }
    }


@router.delete("/{recording_id}")
async def delete_recording(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })

    if item.get("s3_key"):
        try:
            s3.delete_object(Bucket=BUCKET, Key=item["s3_key"])
        except Exception:
            pass

    status_table.delete_item(Key={"raw_id": recording_id})

    return {"success": True, "message": "Deleted successfully"}

@router.patch("/{recording_id}")
async def update_recording(recording_id: str, request: UpdateRecordingRequest):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })

    status_table.update_item(
        Key={"raw_id": recording_id},
        UpdateExpression="SET title = :t",
        ExpressionAttributeValues={":t": request.title}
    )

    return {
        "success": True,
        "data": {"id": recording_id, "title": request.title}
    }

@router.post("/{recording_id}/process")
async def start_processing(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": f"{recording_id} không tồn tại"
        })

    current_status = item.get("status", "")
    if current_status == "completed":
        raise HTTPException(status_code=400, detail={
            "code": "ALREADY_COMPLETED",
            "message": "Recording đã xử lý xong, không cần chạy lại"
        })
    if current_status == "processing":
        raise HTTPException(status_code=400, detail={
            "code": "ALREADY_PROCESSING",
            "message": "Recording đang được xử lý"
        })

    transcript_id = item.get("text_id")
    process_audio_task.delay(
        recording_id=recording_id,
        transcript_id=transcript_id,
        file_name=item["fileName"]
    )

    return {
        "success": True,
        "data": {"id": recording_id, "status": "queued"}
    }


@router.get("/{recording_id}/status")
async def get_status(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code":    "NOT_FOUND",
            "message": f"{recording_id} không tồn tại"
        })

    return {
        "success": True,
        "data": {
            "id":       recording_id,
            "status":   item.get("status",   "unknown"),
            "progress": item.get("progress", 0),
            "stage":    item.get("stage",    ""),
        }
    }



@router.get("/{recording_id}/transcript")
async def get_transcript(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })

    text_id = item.get("text_id")
    if not text_id:
        raise HTTPException(status_code=400, detail={
            "code": "NO_TRANSCRIPT", "message": "Chưa có transcript"
        })

    text_folder = os.getenv("TEXT_BUCKET_FOLDER")
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=f"{text_folder}/{text_id}.json")
        raw = obj["Body"].read().decode("utf-8")
        data = json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail={
            "code": "TRANSCRIPT_NOT_FOUND", "message": str(e)
        })

    results = data.get("results", {})
    transcript_text = results.get("transcripts", [{}])[0].get("transcript", "")

    items = []
    for i, seg in enumerate(results.get("speaker_labels", {}).get("segments", [])):
        items.append({
            "id":       str(i),
            "speaker":  seg.get("speaker_label", "Speaker"),
            "startSec": float(seg.get("start_time", 0)),
            "endSec":   float(seg.get("end_time", 0)),
            "text":     "",
            "tag":      None,
        })

    if not items:
        items = [{"id": "0", "speaker": None, "startSec": 0,
                  "endSec": 0, "text": transcript_text, "tag": None}]

    return {"success": True, "data": {"items": items}}

@router.get("/{recording_id}/summary")
async def get_summary(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })

    if item.get("status") != "completed":
        raise HTTPException(status_code=400, detail={
            "code": "NOT_READY", "message": "Recording chưa xử lý xong"
        })

    segments_prefix = os.getenv("SEGMENTS_PREFIX")

    try:
        obj  = s3.get_object(Bucket=BUCKET, Key=f"{segments_prefix}/{recording_id}.json")
        data = json.loads(obj["Body"].read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=404, detail={
            "code": "SUMMARY_NOT_FOUND", "message": str(e)
        })

    return {
        "success": True,
        "data": {
            "globalSummary": data.get("global_summary", ""),
            "segments": [
                {
                    "index":      s["segment_idx"],
                    "topicLabel": s["topic_label"],
                    "summary":    s["summary"],
                }
                for s in data.get("segments", [])
            ]
        }
    }

@router.get("/{recording_id}/assistant")
async def get_chat_history(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })

    memory = mem_module.load_memory(recording_id)

    if not memory:
        return {
            "success": True,
            "data": {"items": [], "summary": ""}
        }

    history = list(memory.chat_history)
    sources = list(memory.sources)

    items = []
    for i in range(0, len(history) - 1, 2):
        user_msg      = history[i]
        assistant_msg = history[i + 1] if i + 1 < len(history) else None
        turn_idx = i // 2
        turn_sources = sources[turn_idx]["sources"] if turn_idx < len(sources) else []

        items.append({
            "question": user_msg.get("content", ""),
            "answer":   assistant_msg.get("content", "") if assistant_msg else "",
            "sources":  turn_sources,
        })

    return {
        "success": True,
        "data": {
            "items":   items,
            "summary": memory.summary,
        }
    }

@router.delete("/{recording_id}/assistant")
async def delete_chat_history(recording_id: str):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code": "NOT_FOUND", "message": "Recording không tồn tại"
        })


    fresh_memory = mem_module.Memory(raw_id=recording_id)
    mem_module.save_memory(fresh_memory)

    return {
        "success": True,
        "message": "Chat history cleared"
    }


@router.post("/{recording_id}/assistant/query")
async def query_assistant(recording_id: str, request: QueryRequest):
    res  = status_table.get_item(Key={"raw_id": recording_id})
    item = res.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail={
            "code":    "NOT_FOUND",
            "message": "Recording không tồn tại"
        })

    if item.get("status") != "completed":
        raise HTTPException(status_code=400, detail={
            "code":    "NOT_READY",
            "message": "Recording chưa xử lý xong"
        })

    memory = mem_module.load_memory(recording_id)
    if not memory:
        memory = mem_module.Memory(raw_id=recording_id)

    answer = mem_module.chat(memory, request.message)
    mem_module.save_memory(memory)

    current_sources = list(memory.sources)[-1]["sources"] if memory.sources else []

    return {
        "success": True,
        "data": {
            "answer":  answer,
            "sources": current_sources,
        }
    }

