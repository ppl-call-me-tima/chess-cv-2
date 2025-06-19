import cv2

def annotate_warped_pieces(image, xy):
    for i in range(len(xy)):
        cv2.circle(image, xy[i], 2, (0,255,0), -1)
