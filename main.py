import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="dimensions.env", override=True)

from ultralytics import YOLO
# import cv2
import numpy as np
import winsound
import pygame
import asyncio

from constants import WINDOW_WIDTH, WINDOW_HEIGHT

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.position import Position
from helpers.misc import *

from helpers.annotate.warped_corners import annotate_warped_corners
from helpers.annotate.warped_pieces import annotate_warped_pieces

from helpers.detection.detect_corners import detect_corners
from helpers.detection.detect_pieces import detect_pieces

from helpers.engine_analysis.eval_bar import draw_eval_bar
from helpers.engine_analysis.shared_resource import shared_resource
from helpers.engine_analysis.constants import *

from logger import log
from lichess import make_move, set_credentials

from screen_manager import ScreenManager
from ui.screens.menu_screen import MenuScreen
from ui.screens.detect_screen import DetectScreen

# BOARD_PADDING = int(os.environ.get("BOARD_PADDING"))
# BOARD_DIMENSION = int(os.environ.get("BOARD_DIMENSION"))

# WINDOW_WIDTH = 1280
# WINDOW_HEIGHT = 720

# N = BOARD_DIMENSION + 2 * BOARD_PADDING

# BOARD_POINTS = np.array([
#     (0, 0),
#     (N, 0),
#     (N, N),
#     (0, N)
# ])

# def detection_results(image, corner_model, piece_model):
#     corners = detect_corners(corner_model, image, annotate=True)
#     piece_xy, piece_class = detect_pieces(piece_model, image, annotate=True)
    
#     return corners, piece_xy, piece_class

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("ChessCV")

    screen_manager = ScreenManager(screen)
    screen_manager.add_screen("menu", MenuScreen(screen_manager))
    screen_manager.add_screen("detect", DetectScreen(screen_manager))

    # position = await Position().create()

    # started = False
    # not_found = corners_not_detected()

    # play_on_lichess = False
    # lichess_colour = True  # white default

    screen_manager.set_screen("menu")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            screen_manager.handle_event(event)
        
        screen_manager.update()
        screen.fill((30, 30, 30))
        screen_manager.draw(screen)

        pygame.display.flip()

        continue

        # if not started:
        #     standard = input("Does the game start from standard positition? (y/n): ")
        #     if standard.lower() == "y":
        #         castling_fen = "KQkq"
        #     else:
        #         castling_fen = get_castling_fen_from_menu()

        #     started = True
        castling_fen = "KQkq"
        # TODO: remove

        # corners, piece_xy, piece_class = detection_results(image, corner_model, piece_model)
        corners = None
        piece_xy = None
        piece_class = None
        # TODO: remove

        if corners is None:
            # no-corner frame after valid frame
            # if cv2.getWindowProperty("no_corners", cv2.WND_PROP_VISIBLE) == 0:
            #     cv2.destroyAllWindows()
            #     cv2.imshow("no_corners", not_found)
            pass
        else:
            # valid frame after no-corner frame
            # if cv2.getWindowProperty("no_corners", cv2.WND_PROP_VISIBLE) > 0:
            #     cv2.destroyWindow("no_corners")
            
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped_xy = transformer.transform_points(piece_xy)
            warped = transformer.warp_image(image, N)
            
            current_chess = Chessboard(warped_xy, piece_class, N)
            current_chess.rotate_anticlockwise()
            
            if position.current_matrix == []:
                position.set_fen(current_chess.FEN(), castling_fen)
            
            if not position.is_initial_set():
                # if not position.is_valid():
                #     cv2.putText(image, "Position is INVALID", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # cv2.putText(image, "Correct BOARD detected? (y/n): ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # cv2.imshow("image", image)
                # cv2.imshow("board", position.get_board())
                
                # key = cv2.waitKey(20) & 0xFF
                
                # if key == ord("y") and position.is_valid():
                #     position.set_initial(True)
                #     cv2.destroyAllWindows()
                # elif key == ord("n"):
                #     position.clear()
                #     continue
                # elif key == 27:
                #     break
                # else:
                #     continue
                pass

            annotate_warped_corners(warped, N)
            annotate_warped_pieces(warped, warped_xy)
                        
            # if not play_on_lichess:
            #     cv2.putText(image, "Connect lichess: (L)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # cv2.imshow("warped", warped)
            # cv2.imshow("image", image)
            
            valid, new_move_pushed, turn = position.is_next_position_valid(current_chess.FEN())
            
            if valid:
                # cv2.imshow("board", position.get_board())
                
                if play_on_lichess and new_move_pushed:
                    if turn == lichess_colour:
                        make_move(new_move_pushed)
                    else:
                        winsound.Beep(2500, 100)

        # key = cv2.waitKey(1)
        
        # if key == ord("r"):
        #     position.set_initial(False)
        #     play_on_lichess = False
        #     started = False
        # elif key == ord("l"):
        #     if not play_on_lichess:
        #         await set_credentials()
        #     play_on_lichess = not play_on_lichess
        #     lichess_colour = position.chess.turn
        # elif key == ord("e"):
        #     if position.engine_on:
        #         pygame.quit()
        #     else:
        #         pygame.init()
        #         screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #         pygame.display.set_caption("Async Chess Eval")
            
        #     position.toggle_engine()
        # elif key == 8:
        #     position.undo_move()
        #     cv2.imshow("board", position.get_board())
        # elif key == 27:
        #     log(position.chess.fen())
        #     break

        # if position.engine_on:
        #     draw_eval_bar(screen, shared_resource["score"], shared_resource["is_mate"], shared_resource["winning"])
        #     pygame.display.flip()

        # await asyncio.sleep(1/60)
    
    # await position.quit()

if __name__ == "__main__":
    asyncio.run(main())
