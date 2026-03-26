# api/routers/users.py
from fastapi import APIRouter
import boto3, os

router = APIRouter(prefix="/api")
dynamodb = boto3.resource("dynamodb", os.getenv("REGION"))

@router.get("/me")
async def get_me():
    return {
        "success": True,
        "data": {
            "id": "u_001",
            "email": "user@example.com",
            "fullName": "User",
            "avatarUrl": None,
        }
    }