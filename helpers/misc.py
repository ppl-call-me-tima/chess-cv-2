import cv2
import numpy as np

def sort_points_by_angle(pts):
    # Calculate centroid
    center = pts.mean(axis=0)

    # Calculate angles
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])

    sorted_indices = np.argsort(angles)
    return pts[sorted_indices]

def corners_not_detected():
    text = "Corners\nNot\nDetected"
    font = cv2.FONT_HERSHEY_COMPLEX
    scale = 2
    thickness = 2
    color = (255, 255, 255)
    
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    
    x, y0 = (0, 50)
    line_height = text_size[1] + 5
    
    img = np.zeros((350, 350), np.uint8)
    
    for i, line in enumerate(text.split("\n")):
        y = y0 + i * line_height
        cv2.putText(img, line, (x, y), font, scale, color, thickness)
    
    return img
