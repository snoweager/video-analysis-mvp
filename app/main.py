# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json
from datetime import datetime

from .ingestion import start_camera_thread
from .database import Base, engine, SessionLocal
from .models import Camera, Event
from .schemas import (
    CameraCreate,
    CameraResponse,
    EventResponse
)

Base.metadata.create_all(bind=engine)

app = FastAPI()


# ---------- DB DEPENDENCY ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- HEALTH ----------

@app.get("/")
def root():
    return {"status": "ok"}


# ---------- CAMERAS ----------

@app.post("/cameras", response_model=CameraResponse)
def add_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    cam = Camera(
        name=camera.name,
        location=camera.location,
        rtsp_url=camera.rtsp_url,
        status="offline",
        fps=0.0,
        last_frame_time=None,
        zones=json.dumps(camera.zones) if camera.zones else None
    )

    db.add(cam)
    db.commit()
    db.refresh(cam)

    # Start ingestion AFTER DB commit
    start_camera_thread(cam.id)

    return cam


@app.get("/cameras", response_model=list[CameraResponse])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()


# ---------- EVENTS ----------

@app.get("/events", response_model=list[EventResponse])
def list_events(
    camera_id: Optional[int] = None,
    rule: Optional[str] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Event)

    if camera_id:
        query = query.filter(Event.camera_id == camera_id)
    if rule:
        query = query.filter(Event.rule == rule)
    if from_time:
        query = query.filter(Event.timestamp >= from_time)
    if to_time:
        query = query.filter(Event.timestamp <= to_time)

    return query.order_by(Event.timestamp.desc()).all()


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return {"error": "Event not found"}

    return event
