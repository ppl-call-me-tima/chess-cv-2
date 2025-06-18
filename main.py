from ultralytics import YOLO
import cv2
import numpy as np
import argparse
import supervision as sv

from helpers.perspective_transform import PerspectiveTransformer
from helpers.corner_detection1 import get_corners
from helpers.corner_detection2 import get_chessboard_corners
from helpers.misc import *

from helpers.annotate.corners import annotate_corners

PADDING = 33
N = 800 + 2 * PADDING

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
        sorted_corners = sort_points_by_angle(corners)

        transformer = PerspectiveTransformer(sorted_corners, BOARD_POINTS)
        # transformed_points = transformer.transform_points(pieces_xy)
        warped = transformer.warped_image(image, N)
        # cv2.imshow("Warped Image", warped)

        for i in range(len(sorted_corners)):
            corner = tuple(sorted_corners[i].astype(int))
            cv2.circle(image, corner, 10, (0, 255, 0), -1)
            cv2.putText(image, f"{i} : ({corner[0]}, {corner[1]})", corner, 1, 1, (255, 255, 255), 1)

        return warped

def detect_pieces(piece_model, image):
    result = piece_model.predict(image, conf=0.5, device=0)
    detections = sv.Detections.from_ultralytics(result[0])

    piece_xy = detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER).astype(int)
    piece_class = detections.data["class_name"]

    for i in range(len(piece_xy)):
        coods = piece_xy[i]
        cv2.circle(image, coods, 5, (255,0,0), -1)
        cv2.putText(image, f"{piece_class[i]}", coods, 0, 1, (0,0,0), 1)
    
    return piece_xy

def main():
    cap = init_cap()
    
    corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
    piece_model = YOLO(r"runs_piece_detection\content\runs\detect\train\weights\best.pt")

    while True:
        # ret, image = cap.read()
        image = cv2.imread(r"images\2.png")
        
        warped = detect_corners(corner_model, image)
        xy = detect_pieces(piece_model, image)
        
        annotate_corners(warped)
        cv2.imwrite("images\warped.jpg", warped)
        
        cv2.imshow("final image", image)
        cv2.imshow("warped", warped)
        if cv2.waitKey(20) == 27:
            break

if __name__ == "__main__":
    main()
