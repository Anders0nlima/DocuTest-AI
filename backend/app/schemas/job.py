from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime
from app.schemas.generation import GenerationResult

class JobStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobBase(BaseModel):
    filename: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    status: JobStatus
    created_at: datetime
    result: Optional[GenerationResult] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True
