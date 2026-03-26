from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    message: str
    includeContext: Optional[bool] = True

class UploadUrlRequest(BaseModel):
    fileName: str
    contentType: str
    fileSize: int
    durationSec:int

class ProcessRequest(BaseModel):
    fileUrl: str

class UpdateRecordingRequest(BaseModel):
    title: str

class CreateRecordingRequest(BaseModel):
    fileName: str
    s3Key:    str
    title:    Optional[str] = None