# app/rules.py
import cv2
import numpy as np

def point_in_polygon(point, polygon):
    """
    point: (x, y)
    polygon: [[x1,y1], [x2,y2], ...]
    """
    poly_np = np.array(polygon, dtype=np.int32)
    return cv2.pointPolygonTest(poly_np, point, False) >= 0
