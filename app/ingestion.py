# app/ingestion.py

import cv2
import time
import threading
import json
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.yolo import model, ALLOWED_CLASSES
from .database import SessionLocal
from .models import Camera, Event


latest_frames = {}
YOLO_FRAME_SKIP = 5

SNAPSHOT_DIR = "data/snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def point_in_polygon(point, polygon):
    import numpy as np
    poly = np.array(polygon, dtype="int32")
    return cv2.pointPolygonTest(poly, point, False) >= 0


def save_snapshot(frame):
    filename = f"evt_{uuid.uuid4().hex}.jpg"
    path = os.path.join(SNAPSHOT_DIR, filename)
    cv2.imwrite(path, frame)
    return path


def camera_worker(camera_id: int):
    while True:
        db: Session = SessionLocal()
        camera = db.query(Camera).filter(Camera.id == camera_id).first()

        if camera is None:
            db.close()
            return

        # Webcam fallback
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            camera.status = "offline"
            db.commit()
            db.close()
            time.sleep(5)
            continue

        camera.status = "online"
        db.commit()

        # Parse zones once
        zones = json.loads(camera.zones) if camera.zones else None

        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                camera.status = "offline"
                db.commit()
                break

            frame_count += 1
            latest_frames[camera_id] = frame
            camera.last_frame_time = datetime.utcnow()
            db.commit()

            if frame_count % YOLO_FRAME_SKIP == 0:
                results = model(frame, verbose=False)

                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = model.names[cls_id]
                        conf = float(box.conf[0])

                        if cls_name != "person":
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        if not zones:
                            continue

                        for zone in zones["zones"]:
                            if point_in_polygon((cx, cy), zone["points"]):
                                snapshot_path = save_snapshot(frame)

                                event = Event(
                                    camera_id=camera_id,
                                    rule="intrusion",
                                    object_type="person",
                                    confidence=conf,
                                    bbox=json.dumps([x1, y1, x2, y2]),
                                    snapshot_path=snapshot_path
                                )

                                db.add(event)
                                db.commit()

                                print(f"🚨 INTRUSION on Camera {camera_id}")

            time.sleep(0.05)

        cap.release()
        db.close()
        time.sleep(2)


def start_camera_thread(camera_id: int):
    thread = threading.Thread(
        target=camera_worker,
        args=(camera_id,),
        daemon=True
    )
    thread.start()
