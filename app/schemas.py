# app/schemas.py

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# ---------- CAMERAS ----------

class CameraCreate(BaseModel):
    name: str
    location: Optional[str] = None
    rtsp_url: str
    zones: Optional[Dict[str, Any]] = None


class CameraResponse(BaseModel):
    id: int
    name: str
    location: Optional[str]
    rtsp_url: str
    status: str
    fps: float
    last_frame_time: Optional[datetime]
    zones: Optional[str]

    class Config:
        from_attributes = True


# ---------- EVENTS ----------

class EventResponse(BaseModel):
    id: int
    camera_id: int
    timestamp: datetime
    rule: str
    object_type: str
    confidence: float
    bbox: str
    snapshot_path: str

    class Config:
        from_attributes = True
