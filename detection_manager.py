from ultralytics import YOLO

from constants import BOARD_POINTS, N
from helpers.misc import init_cap

from helpers.perspective_transform import PerspectiveTransformer
from helpers.chessboard import Chessboard
from helpers.position import Position

from helpers.detection.detect_corners import detect_corners
from helpers.detection.detect_pieces import detect_pieces

class DetectionManger:
    def __init__(self):
        self.cap = init_cap()
        self.image = None

        self.corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
        self.piece_model = YOLO(r"runs_piece_detection_improved1\content\runs\detect\train\weights\best.pt")

        self.position = Position()

    def make_detection(self):
        """
        Perform detection for the particular frame and update the class variables
        that might be required for making detections along the way or externally at detect_screen.py
        """

        ret, self.image = self.cap.read()

        corners = detect_corners(self.corner_model, self.image, annotate=True)
        piece_coods, piece_class = detect_pieces(self.piece_model, self.image, annotate=True)

        if corners is not None:
            transformer = PerspectiveTransformer(corners, BOARD_POINTS)
            warped_coods = transformer.transform_points(piece_coods)
            # warped_image = transformer.warp_image(self.image, N)

            current_chess = Chessboard(warped_coods, piece_class, N)
            current_chess.rotate_anticlockwise()

            if not self.position.is_initial_set():
                self.position.set_fen(current_chess.FEN(), "KQkq")

        # print("fen:", self.position.chess.fen())

    def get_board(self):
        return self.position.get_board()

    def get_feed(self):
        return self.image

    def set_position_initial_state(self, status: bool):
        self.position.set_initial(status)
