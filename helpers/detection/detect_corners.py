from helpers.detection.corner_detection2 import get_chessboard_corners
from helpers.misc import sort_points_by_angle
from helpers.annotate.corners import annotate_corners

def detect_corners(corner_model, image, annotate=False):
    result = corner_model.predict(image, conf=0.5, device=0)
    corners = get_chessboard_corners(result[0], image)
    
    if corners is not None:
        corners = sort_points_by_angle(corners)
        
    if corners is not None and annotate:
        annotate_corners(image, corners)

    return corners
