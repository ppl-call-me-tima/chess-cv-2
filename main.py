from ultralytics import YOLO
import cv2
import numpy as np

from helpers.perspective_transform import PerspectiveTransformer
from helpers.corner_detection import get_corners
from helpers.misc import *

model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
image = cv2.imread(r"images\5.png")
result = model.predict(image, conf=0.5, device=0)

result[0].show()

PADDING = 33
N = 800 + 2 * PADDING

BOARD_POINTS = np.array([
    (0, 0),
    (N, 0),
    (N, N),
    (0, N)
])

corners = get_corners(result[0], image)
sorted_corners = sort_points_by_angle(corners)

transformer = PerspectiveTransformer(sorted_corners, BOARD_POINTS)
# transformed_points = transformer.transform_points(pieces_xy)
warped = transformer.warped_image(image, N)
cv2.imwrite("images\warped.jpg", warped)

cv2.imshow("Warped Image", warped)

if sorted_corners is not None:
    viz_image = image.copy()
    for i in range(len(sorted_corners)):
        corner = tuple(sorted_corners[i].astype(int))
        cv2.circle(viz_image, corner, 10, (0, 255, 0), -1)
        cv2.putText(
            viz_image, f"{i} : ({corner[0]}, {corner[1]})", corner, 1, 1, (255, 255, 255), 1)
    cv2.imshow("Final Corners", viz_image)
    cv2.waitKey(0)
else:
    print("Could not approximate to a 4-sided polygon.")
