import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env")

from ultralytics import YOLO
import cv2
import numpy as np

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.misc import *

from helpers.annotate.warped_corners import annotate_warped_corners
from helpers.annotate.warped_pieces import annotate_warped_pieces

from helpers.detection.detect_corners import detect_corners
from helpers.detection.detect_pieces import detect_pieces

BOARD_PADDING = int(os.environ.get("BOARD_PADDING"))
BOARD_DIMENSION = int(os.environ.get("BOARD_DIMENSION"))

N = BOARD_DIMENSION + 2 * BOARD_PADDING

BOARD_POINTS = np.array([
    (0, 0),
    (N, 0),
    (N, N),
    (0, N)
])

def main():
    cap = init_cap()
    
    corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
    piece_model = YOLO(r"runs_piece_detection\content\runs\detect\train\weights\best.pt")

    not_found = corners_not_detected()

    while True:
        # ret, image = cap.read()
        image = cv2.imread(r"images\1.png")
        
        corners = detect_corners(corner_model, image, annotate=True)
        piece_xy, piece_class = detect_pieces(piece_model, image, annotate=True)
        
        if corners is None:
            cv2.imshow("Corners Not Detected", not_found)
        else:
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped = transformer.warp_image(image, N)
            warped_xy = transformer.transform_points(piece_xy)
            
            chess = Chessboard(warped_xy, piece_class, N)
            chess.rotate_anticlockwise()
            board = chess.chessboard()
            
            annotate_warped_corners(warped, N)
            annotate_warped_pieces(warped, warped_xy)
            
            # cv2.imwrite("images\warped2.jpg", warped)
            # cv2.imwrite("images\board2.jpg", board)
            
            cv2.imshow("final image", image)
            cv2.imshow("warped", warped)
            cv2.imshow("board", board)
        
        if cv2.waitKey(20) == 27:
            break

if __name__ == "__main__":
    main()
