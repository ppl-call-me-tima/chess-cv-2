import cv2

def annotate_pieces(image, piece_xy, piece_class):
    for i in range(len(piece_xy)):
            cv2.circle(image, piece_xy[i], 5, (255,0,0), -1)
            cv2.putText(image, f"{piece_class[i]}", piece_xy[i], 0, 1, (0,0,0), 1)
