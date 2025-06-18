import os
import cv2

def annotate_corners(img, N):
    PADDING = int(os.environ.get("BOARD_PADDING"))
    DELTA = int(os.environ.get("SQUARE_DIMENSION"))
    END = N - PADDING + 1
    
    for y in range(PADDING, END, DELTA):
        for x in range(PADDING, END, DELTA):
            cv2.circle(img, (x, y), 5, (0,0,255), -1)
