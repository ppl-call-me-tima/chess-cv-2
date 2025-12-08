import argparse
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


def init_cap():
    parser = argparse.ArgumentParser(description="argeparse_desc")
    parser.add_argument("--webcam-resolution", default=[1280, 720], nargs=2, type=int)
    args = parser.parse_args()
    
    frame_width, frame_height = args.webcam_resolution
    
    cap = cv2.VideoCapture(0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    return cap

def get_castling_fen_from_menu():
    K = input("Can white castle on king side? (y/n): ")
    Q = input("Can white castle on queen side? (y/n): ")
    k = input("Can black castle on king side? (y/n): ")
    q = input("Can black castle on queen side? (y/n): ")
    
    castling_fen = ""
    
    if K.lower() == "y": castling_fen += "K"
    if Q.lower() == "y": castling_fen += "Q"
    if k.lower() == "y": castling_fen += "k"
    if q.lower() == "y": castling_fen += "q"

    return castling_fen

def cv2pygame(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.transpose(image)
    # image = cv2.flip(image, 0)
    return image
