import cv2

def annotate_pieces(image, xy):
    for i in range(len(xy)):
        cood = xy[i]
        cv2.circle(image, (cood[0], cood[1]), 2, (0,255,0), -1)
