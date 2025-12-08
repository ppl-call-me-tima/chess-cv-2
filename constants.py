import numpy as np
import os

BOARD_PADDING = int(os.environ.get("BOARD_PADDING"))
BOARD_DIMENSION = int(os.environ.get("BOARD_DIMENSION"))

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

N = BOARD_DIMENSION + 2 * BOARD_PADDING

BOARD_POINTS = np.array([
    (0, 0),
    (N, 0),
    (N, N),
    (0, N)
])
