import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env")

from ultralytics import YOLO
import cv2
import numpy as np
import argparse
import supervision as sv

from helpers.perspective_transform import PerspectiveTransformer
from helpers.corner_detection2 import get_chessboard_corners
from helpers.chessboard import Chessboard
from helpers.misc import *

from helpers.annotate.corners import annotate_corners
from helpers.annotate.pieces import annotate_pieces

BOARD_PADDING = int(os.environ.get("BOARD_PADDING"))
BOARD_DIMENSION = int(os.environ.get("BOARD_DIMENSION"))

N = BOARD_DIMENSION + 2 * BOARD_PADDING

BOARD_POINTS = np.array([
    (0, 0),
    (N, 0),
    (N, N),
    (0, N)
])

def init_cap():
    parser = argparse.ArgumentParser(description="argeparse_desc")
    parser.add_argument("--webcam-resolution", default=[1280, 720], nargs=2, type=int)
    args = parser.parse_args()
    
    frame_width, frame_height = args.webcam_resolution
    
    cap = cv2.VideoCapture(1)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    return cap

def detect_corners(corner_model, image):
    result = corner_model.predict(image, conf=0.5, device=0)

    corners = get_chessboard_corners(result[0], image)
    
    if corners is not None:
        corners = sort_points_by_angle(corners)
        
        for i in range(len(corners)):
            corner = tuple(corners[i])
            cv2.circle(image, corner, 10, (0, 255, 0), -1)
            cv2.putText(image, f"{i} : ({corner[0]}, {corner[1]})", corner, 1, 1, (255, 255, 255), 1)

    return corners

def detect_pieces(piece_model, image):
    result = piece_model.predict(image, conf=0.5, device=0)
    detections = sv.Detections.from_ultralytics(result[0])

    piece_xy = detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER).astype(int)
    piece_class = detections.data["class_name"]

    for i in range(len(piece_xy)):
        coods = piece_xy[i]
        cv2.circle(image, coods, 5, (255,0,0), -1)
        cv2.putText(image, f"{piece_class[i]}", coods, 0, 1, (0,0,0), 1)
    
    return piece_xy, piece_class

def main():
    cap = init_cap()
    
    corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
    piece_model = YOLO(r"runs_piece_detection\content\runs\detect\train\weights\best.pt")

    not_found = corners_not_detected()

    while True:
        # ret, image = cap.read()
        image = cv2.imread(r"C:\Users\2648a\Pictures\Camera Roll\WIN_20250619_04_08_37_Pro.jpg")
        
        corners = detect_corners(corner_model, image)
        piece_xy, piece_class = detect_pieces(piece_model, image)
        
        if corners is None:
            cv2.imshow("Corners Not Detected", not_found)
        else:
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped = transformer.warp_image(image, N)
            warped_xy = transformer.transform_points(piece_xy)
            
            chess = Chessboard(warped_xy, piece_class, N)
            board = chess.chessboard()
            
            annotate_corners(warped, N)
            annotate_pieces(warped, warped_xy)
            
            # cv2.imwrite("images\warped2.jpg", warped)
            # cv2.imwrite("images\board2.jpg", board)
            
            cv2.imshow("final image", image)
            cv2.imshow("warped", warped)
            cv2.imshow("board", board)
        
        if cv2.waitKey(20) == 27:
            break

if __name__ == "__main__":
    main()
