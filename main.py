import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env")

from ultralytics import YOLO
import cv2
import numpy as np

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.position import Position
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
    corners_previously_existed = False
    position = Position()

    while True:
        ret, image = cap.read()
        # image = cv2.imread(r"images\1.png")
        
        corners = detect_corners(corner_model, image, annotate=True)
        piece_xy, piece_class = detect_pieces(piece_model, image, annotate=True)
        
        if corners is None:
            if corners_previously_existed:
                corners_previously_existed = False
                cv2.destroyAllWindows()

            cv2.imshow("no_corners", not_found)
        else:
            if not corners_previously_existed:
                cv2.destroyWindow("no_corners")
                corners_previously_existed = True
            
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped_xy = transformer.transform_points(piece_xy)
            warped = transformer.warp_image(image, N)
            
            chess = Chessboard(warped_xy, piece_class, N)
            chess.rotate_anticlockwise()
            
            if position.current_board is None:
                position.set_fen_board(chess.FEN(), chess.chessboard())
            
            if not position.is_initial_set():
                if not position.is_valid():
                    cv2.putText(image, "Position is INVALID", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.putText(image, "Correct position detected? (y/n): ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow("image", image)
                cv2.imshow("board", position.get_board())
                
                key = cv2.waitKey(20) & 0xFF
                
                if key == ord("y") and position.is_valid():
                    position.set_initial(True)
                    cv2.destroyAllWindows()
                elif key == ord("n"):
                    position.clear()
                    continue
                elif key == 27:
                    break
                else:
                    continue
                        
            annotate_warped_corners(warped, N)
            annotate_warped_pieces(warped, warped_xy)
            
            # cv2.imwrite("images\warped2.jpg", warped)
            # cv2.imwrite("images\board2.jpg", board)
            
            cv2.imshow("warped", warped)
            cv2.imshow("image", image)
            
            if position.is_next_position_valid(chess.FEN(), chess.chessboard()):
                cv2.imshow("board", position.get_board())
        
        key = cv2.waitKey(20)
        
        if key == ord("r"):
            position.set_initial(False)
        elif key == 27:
            break

if __name__ == "__main__":
    main()
