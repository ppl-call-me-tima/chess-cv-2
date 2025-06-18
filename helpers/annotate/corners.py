import cv2

def annotate_corners(img):
    PADDING = 33
    DELTA = 100
    END = img.shape[0]
    
    for x in range(PADDING, END - PADDING + 1, DELTA):
        for y in range(PADDING, END - PADDING + 1, DELTA):
            cv2.circle(img, (x, y), 5, (0,0,255), -1)
