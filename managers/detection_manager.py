from ultralytics import YOLO
import winsound

from constants import BOARD_POINTS, N
from managers.lichess_manager import LichessManager
from managers.camera_manager import CameraManager
from helpers.misc import init_cap

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.position import Position

from helpers.detection.detect_corners import detect_corners
from helpers.detection.detect_pieces import detect_pieces

class DetectionManger:
    def __init__(self, camera_manager: CameraManager):
        self.cap = init_cap()
        self.image = None

        self.corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
        self.piece_model = YOLO(r"runs_piece_detection_improved1\content\runs\detect\train\weights\best.pt")

        self.position = Position()
        self.camera_manager = camera_manager

    def make_detection(self, lichess_manager: LichessManager):
        """
        Perform detection for the particular frame and update the class variables
        that might be required for making detections along the way or externally at detect_screen.py
        """

        frame = self.camera_manager.get_frame()
        if frame is None:
            return
        
        self.image = frame
        corners = detect_corners(self.corner_model, self.image, annotate=True)
        piece_coods, piece_class = detect_pieces(self.piece_model, self.image, annotate=True)

        if corners is not None:
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped_coods = transformer.transform_points(piece_coods)
            # warped_image = transformer.warp_image(self.image, N)

            current_chess = Chessboard(warped_coods, piece_class, N)
            current_chess.rotate_anticlockwise()

            if not self.position.is_initial_set():
                #TODO: fix hard-code castling rights
                self.position.set_fen(current_chess.FEN(), "KQkq")
            else:
                valid, pushed_move, turn = self.position.is_next_position_valid(current_chess.FEN())

                if lichess_manager.is_lichess_connected() and valid and pushed_move:
                    if turn == lichess_manager.colour:
                        lichess_manager.make_move(pushed_move)
                    else:
                        winsound.Beep(2500, 100)

        # print("fen:", self.position.chess.fen())

    def get_feed(self):
        return self.image
