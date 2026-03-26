# api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import recordings, users
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI(title="Voice Summarizer API")

# CORS — cho phép FE gọi vào
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # đổi thành domain FE khi production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Đăng ký routers
app.include_router(recordings.router)
app.include_router(users.router)

# Bắt lỗi không lường trước — không để server crash
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc)
            }
        }
    )