# app/yolo.py
from ultralytics import YOLO

# Load model ONCE at startup
model = YOLO("yolov8n.pt")

# Allowed classes
ALLOWED_CLASSES = {"person", "car"}
