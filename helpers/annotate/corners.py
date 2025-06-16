import cv2

img = cv2.imread(r"images\warped.jpg")

PADDING = 33
DELTA = 100
END = img.shape[0]

print(img.shape)

def annotate_corners(img):
    for x in range(PADDING, END - PADDING + 1, DELTA):
        for y in range(PADDING, END - PADDING + 1, DELTA):
            cv2.circle(img, (x, y), 5, (0,0,255), -1)

annotate_corners(img)
cv2.imshow("annotated image", img)
cv2.waitKey(0)
