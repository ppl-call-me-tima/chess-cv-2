import supervision as sv
from helpers.annotate.pieces import annotate_pieces

def detect_pieces(piece_model, image, annotate=False):
    result = piece_model.predict(image, conf=0.60, device=0, iou=0.60)
    detections = sv.Detections.from_ultralytics(result[0])

    piece_xy = detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER).astype(int)
    piece_class = detections.data["class_name"]

    if annotate:
        annotate_pieces(image, piece_xy, piece_class)
    
    return piece_xy, piece_class
