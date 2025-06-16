from ultralytics import YOLO
import cv2
import supervision as sv

model = YOLO(r"runs_piece_detection\content\runs\detect\train\weights\best.pt")
image = cv2.imread(r"images\5.png")
result = model.predict(image, conf=0.5, device=0)
detections = sv.Detections.from_ultralytics(result[0])

print(detections)

piece_xy = detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER).astype(int)
piece_class = detections.data["class_name"]

print(piece_xy)
print(piece_class)

for i in range(len(piece_xy)):
    coods = piece_xy[i]
    cv2.circle(image, coods, 5, (255,0,0), -1)
    cv2.putText(image, f"{piece_class[i]}", coods, 0, 1, (0,0,0), 1)

cv2.imshow("annotated_pieces", image)
cv2.waitKey(0)
