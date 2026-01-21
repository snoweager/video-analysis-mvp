from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect(frame):
    results = model(frame, conf=0.4)
    detections = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls)
            if cls == 0:  # person
                detections.append({
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()
                })
    return detections
