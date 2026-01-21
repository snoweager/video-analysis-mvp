# 🛰️ Multi-Camera Video Analytics Platform — MVP

## 1. Objective

The objective of this project is to build a **working MVP of a multi-camera video analytics platform** that demonstrates end-to-end capabilities commonly found in modern Video Management Systems (VMS) and AI-driven video analytics products.

The system:

* Ingests live camera streams (RTSP / webcam fallback)
* Runs computer vision inference for object detection
* Applies rule-based analytics (zones + intrusion logic)
* Generates and stores events with snapshots
* Exposes REST APIs and a simple web dashboard
* Is architected to scale to multiple cameras and analytics modules

The design and feature choices are inspired by patterns observed in global platforms such as:

* **Milestone** (VMS & centralized camera management)
* **BriefCam** (analytics modules for review/respond/research)
* **Avigilon** (AI alerts and accelerated incident review)
* **Frigate** (local-first processing, zones, event-driven architecture)

---

## 2. Mandatory Scope (Implemented)

### A. Video Ingestion

* Supports multiple camera streams (RTSP or webcam fallback).
* Each stream is treated as a **Camera** entity with:

  * `id`
  * `name`
  * `location`
  * `rtsp_url`
  * `status` (online/offline)
  * `fps` (approximate)
  * `last_frame_time`
* Each camera runs in its own **background ingestion thread**.
* Automatic reconnection logic on stream failure.
* Designed to support 1–N cameras concurrently.

> **Note:** On Windows systems without FFmpeg, webcam (`cv2.VideoCapture(0)`) is used as a fallback for RTSP testing. This is an accepted MVP compromise.

---

### B. Inference & Analytics

* **Object detection** using **YOLOv8n (Ultralytics)**.
* Classes detected (for MVP):

  * `person`
  * `car`
* Inference is run every **N frames** to control CPU usage.
* Latest frames are kept **in memory** for fast access.

#### Zones & Rules

* Zones are defined per camera using **JSON-based polygon definitions**.
* Implemented rule:

  * **Intrusion**: A person enters a restricted zone.
* Zone configuration is stored as JSON and can be edited via the UI.

---

### C. Event Store & API

* Events are persisted in a **SQLite database** (sufficient for MVP).
* Each event contains:

  * `camera_id`
  * `timestamp`
  * `rule`
  * `object_type`
  * `confidence`
  * `bounding_box`
  * `snapshot_path`

#### Implemented REST APIs

* `GET /cameras`
* `POST /cameras`
* `GET /events`

  * Supports filters:

    ```
    /events?camera_id=&rule=&from=&to=
    ```
* `GET /events/{id}`
* `GET /` (health check)

---

### D. Dashboard (UI)

A simple, functional web UI is included to demonstrate system behavior.

The dashboard shows:

* Camera list with **live status**
* Best-effort **live preview** (implemented as periodic snapshots)
* Event feed with filtering
* Event detail view with:

  * Snapshot image
  * Metadata (rule, timestamp, camera, confidence)
* Zone editor using **raw JSON input** (no drawing UI)

> **Design note:**
> Live preview is implemented using periodic frame snapshots rather than continuous streaming to keep the MVP lightweight and browser-compatible. The backend architecture supports future upgrades to MJPEG or WebRTC streaming.

---

### E. Packaging & Run Instructions

#### Tech Stack

* **Backend:** FastAPI, SQLAlchemy
* **CV / AI:** OpenCV, Ultralytics YOLOv8
* **Database:** SQLite
* **Frontend:** Vanilla HTML + JavaScript (fetch API)

#### Setup Instructions

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Open:

* API docs: `http://127.0.0.1:8000/docs`
* UI: `index.html` (served locally)

#### Add a Camera (Example)

```json
POST /cameras
{
  "name": "Demo Camera",
  "location": "Test Lab",
  "rtsp_url": "rtsp://example_stream",
  "zones": {
    "zones": [
      {
        "name": "restricted_area",
        "type": "polygon",
        "points": [[100,100],[400,100],[400,400],[100,400]]
      }
    ]
  }
}
```

---

## 3. Freedom to Add Features (Future Work)

The architecture is designed to support several real-world extensions inspired by global platforms:

### VMS-like Capabilities (Milestone-style)

* Multi-site camera grouping
* Camera onboarding wizard
* Export/import camera configurations
* Role-based access control (Admin / Operator / Viewer)

### Analytics Modules (BriefCam-style)

* Review: post-incident search and filtering
* Respond: real-time alert views
* Research: trends, heatmaps, counters

### AI-Driven Operations (Avigilon-style)

* “Attention required” event prioritization
* Faster review with timeline scrubbing and event jumps

### Local-first & Event Messaging (Frigate-style)

* MQTT / webhook event publishing
* Config-driven rules (YAML/JSON)
* Pre/post-event clip recording

### Performance & Scaling

* Hardware acceleration (OpenVINO / DeepStream)
* Dynamic stream management
* Metrics: FPS, inference latency, queue depth

---

## 4. Architecture Overview

For MVP speed, the system is implemented as a **single FastAPI service**, but internally structured as modular components:

* **Ingestion module**: Pulls frames from camera streams
* **Inference module**: Runs YOLO object detection
* **Rules engine**: Applies zone-based logic
* **API layer**: Stores and serves cameras/events
* **UI**: Lightweight dashboard

This monorepo approach keeps the system easy to understand while remaining extensible.

---

## 5. Deliverables

### Included

* ✅ Git repository with complete source code
* ✅ Working backend + APIs
* ✅ Event storage with snapshots
* ✅ Web dashboard
* ✅ This README

### Optional / Future

* Docker Compose
* Screen recording demo (2–4 min)
* Postman collection
* Automated tests

---

## 6. Known Limitations

* RTSP decoding on Windows may require FFmpeg (webcam fallback used for MVP).
* No authentication or access control (not required for MVP).
* No continuous video storage (event/snapshot-based approach used intentionally).
* UI is functional but intentionally minimal.

---

## 7. What to Highlight in Discussion

1. End-to-end system working under time constraints
2. Thread-per-camera ingestion and reliability handling
3. Modular architecture despite single-service MVP
4. Research-driven feature choices
5. Clear roadmap for scaling, security, and performance

---

## 8. Next Steps (With 2 More Weeks)

* Proper RTSP handling with FFmpeg
* MJPEG / WebRTC live streaming
* Role-based access control
* Event clip export
* Metrics & monitoring
* Multi-model inference pipelines

---

🧠 **Final Note**

This project prioritizes **engineering clarity, reliability, and product thinking** over UI polish. The MVP demonstrates how real-world video analytics systems are structured and scaled, while remaining achievable within a short development window.
