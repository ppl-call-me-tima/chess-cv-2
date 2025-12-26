import cpuinfo
import torch
from ultralytics import YOLO
import supervision as sv

from helpers.detection.corners import get_chessboard_corners, sort_points_by_angle
from helpers.annotate.corners import annotate_corners
from helpers.annotate.pieces import annotate_pieces

class InferenceManager:
    def __init__(self):
        self.device = None
        self.device_list = []

        self.corner_model = YOLO(r"runs_corner_detection\content\runs\segment\train3\weights\best.pt")
        self.piece_model = YOLO(r"runs_piece_detection_improved1\content\runs\detect\train\weights\best.pt")

    def get_device_list(self):
        self.device_list = []

        cpu = cpuinfo.get_cpu_info().get("brand_raw")
        gpu = torch.cuda.is_available()

        if cpu: self.device_list.append(cpu)
        if gpu: self.device_list.append(torch.cuda.get_device_name())
        
        return self.device_list

    def set_device(self, index):
        if 0 <= index < len(self.device_list):
            if index == 0:
                self.device = "cpu"
            elif index == 1:
                self.device = "cuda"

    def detect_corners(self, image, annotate=False):
        result = self.corner_model.predict(image, conf=0.5, device=self.device)
        corners = get_chessboard_corners(result[0], image)
        
        if corners is not None:
            corners = sort_points_by_angle(corners)
            
        if corners is not None and annotate:
            annotate_corners(image, corners)

        return corners

    def detect_pieces(self, image, annotate=False):
        result = self.piece_model.predict(image, conf=0.60, device=self.device, iou=0.60)
        detections = sv.Detections.from_ultralytics(result[0])

        piece_xy = detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER).astype(int)
        piece_class = detections.data["class_name"]

        if annotate:
            annotate_pieces(image, piece_xy, piece_class)
        
        return piece_xy, piece_class
