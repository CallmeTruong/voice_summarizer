from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import recordings, library, health_check
from dotenv import load_dotenv
import os

load_dotenv()
ENV = os.getenv("ENV_MODE")

app = FastAPI(title="Voice Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    docs_url=None if ENV == "prod" else "/docs",
    redoc_url=None if ENV == "prod" else "/redoc",
    openapi_url=None if ENV == "prod" else "/openapi.json",
)

app.include_router(recordings.router)
app.include_router(library.router)
app.include_router(health_check.router)


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