from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from .database import Base

# ---------------- CAMERA ----------------
class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    rtsp_url = Column(String, nullable=False)
    status = Column(String, default="offline")
    fps = Column(Float, default=0.0)
    last_frame_time = Column(DateTime)
    zones = Column(Text)  # JSON string


# ---------------- EVENT ----------------
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rule = Column(String)
    object_type = Column(String)
    confidence = Column(Float)
    bbox = Column(Text)           # JSON
    snapshot_path = Column(String)
