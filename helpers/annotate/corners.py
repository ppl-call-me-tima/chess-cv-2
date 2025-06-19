import cv2

def annotate_corners(image, corners):
    for i in range(len(corners)):
                cv2.circle(image, corners[i], 10, (0, 255, 0), -1)
                cv2.putText(image, f"{i} : ({corners[i]})", corners[i], 1, 1, (255, 255, 255), 1)
