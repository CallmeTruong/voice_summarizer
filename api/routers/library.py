from fastapi import APIRouter, HTTPException
from boto3.dynamodb.conditions import Key, Attr
import boto3, os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/api/library")

dynamodb     = boto3.resource("dynamodb", os.getenv("REGION"))
status_table = dynamodb.Table(os.getenv("HISTORY_TABLE"))
user_table   = dynamodb.Table(os.getenv("USER_TABLE"))


@router.get("")
async def list_recordings(
    user_id: str,
    page: int = 1,
    limit: int = 10,
    status: str = None,
    search: str = None,
):
    res = user_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )
    user_items = res.get("Items", [])

    if not user_items:
        return {"items": [], "total": 0, "page": page, "limit": limit}

    raw_ids = [i["raw_id"] for i in user_items]

    keys = [{"raw_id": rid} for rid in raw_ids]
    batch_res = dynamodb.batch_get_item(
        RequestItems={
            os.getenv("HISTORY_TABLE"): {"Keys": keys}
        }
    )
    items = batch_res["Responses"].get(os.getenv("HISTORY_TABLE"), [])

    if status:
        items = [i for i in items if i.get("status") == status]
    if search:
        search_lower = search.lower()
        items = [
            i for i in items
            if search_lower in i.get("fileName", "").lower()
            or search_lower in i.get("title", "").lower()
        ]

    items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

    total = len(items)
    start = (page - 1) * limit
    page_items = items[start:start + limit]

    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id":           i["raw_id"],
                    "title":        i.get("title", i.get("fileName", "")),
                    "fileName":     i.get("fileName", ""),
                    "status":       i.get("status", "unknown"),
                    "createdAt":    i.get("createdAt", ""),
                    "durationSec":  i.get("durationSec", None),
                    "summaryShort": i.get("summaryShort", ""),
                }
                for i in page_items
            ],
            "total": total,
            "page":  page,
            "limit": limit,
        }
    }