import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env", override=True)

from ultralytics import YOLO
import cv2
import numpy as np
import winsound

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.position import Position
from helpers.misc import *

from helpers.annotate.warped_corners import annotate_warped_corners
from helpers.annotate.warped_pieces import annotate_warped_pieces

from helpers.detection.detect_corners import detect_corners
from helpers.detection.detect_pieces import detect_pieces

from logger import log
from lichess import play_move

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
    piece_model = YOLO(r"runs_piece_detection_improved1\content\runs\detect\train\weights\best.pt")

    started = False
    not_found = corners_not_detected()
    position = Position()
    play_on_lichess = False
    lichess_colour = True  # white default

    while True:
        ret, image = cap.read()
        # image = cv2.imread(r"images\1.png")
        
        if not started:
            standard = input("Does the game start from standard positition? (y/n): ")
            if standard.lower() == "y":
                castling_fen = "KQkq"
            else:
                castling_fen = get_castling_fen_from_menu()

        corners = detect_corners(corner_model, image, annotate=True)
        piece_xy, piece_class = detect_pieces(piece_model, image, annotate=True)
        
        if corners is None:
            if not started:
                corners_previously_existed = False
            
            if corners_previously_existed:
                corners_previously_existed = False
                cv2.destroyAllWindows()

            cv2.imshow("no_corners", not_found)
        else:
            if not started:
                corners_previously_existed = True
            
            if not corners_previously_existed:
                cv2.destroyWindow("no_corners")
                corners_previously_existed = True
            
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped_xy = transformer.transform_points(piece_xy)
            warped = transformer.warp_image(image, N)
            
            chess = Chessboard(warped_xy, piece_class, N)
            chess.rotate_anticlockwise()
            
            if position.current_matrix == []:
                position.set_fen(chess.FEN(), castling_fen)
            
            if not position.is_initial_set():
                if not position.is_valid():
                    cv2.putText(image, "Position is INVALID", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.putText(image, "Correct BOARD detected? (y/n): ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
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
                        
            if not play_on_lichess:
                cv2.putText(image, "Connect lichess: (L)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # cv2.imshow("warped", warped)
            cv2.imshow("image", image)
            
            valid, new_move_pushed, turn = position.is_next_position_valid(chess.FEN())

            if valid and new_move_pushed:
                log(new_move_pushed)
            
            if valid:
                cv2.imshow("board", position.get_board())
                
                if play_on_lichess and new_move_pushed:
                    if turn == lichess_colour:
                        play_move(new_move_pushed)
                    else:
                        winsound.Beep(2500, 100)

        key = cv2.waitKey(20)
        
        if key == ord("r"):
            position.set_initial(False)
            play_on_lichess = False
        elif key == ord("l"):
            if not play_on_lichess:
                lichess_game_id = input("Enter Lichess Game ID: ")
                os.environ["LICHESS_GAME_ID"] = lichess_game_id
            play_on_lichess = not play_on_lichess
            lichess_colour = position.chess.turn
        elif key == 27:
            log(position.chess.fen())
            break
                
        started = True

if __name__ == "__main__":
    main()
