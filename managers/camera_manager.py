import cv2
from cv2_enumerate_cameras import enumerate_cameras

class CameraManager:
    def __init__(self):
        self.cap = None
        self.index = None
        self.indices_set = set()
    
    def set_index(self, index):
        self.index = index

    def get_camera_list(self):
        self.camera_list = [(cam.index, cam.name) for cam in enumerate_cameras(cv2.CAP_MSMF)]
        return self.camera_list

    def set_camera(self, index):
        indices_set = set()
        for ind, _ in self.camera_list:
            indices_set.add(ind)

        if index in indices_set:
            if self.index == index and self.cap is not None and self.cap.isOpened():
                return True

            if self.cap is not None:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(index=index, apiPreference=cv2.CAP_MSMF)
            if self.cap.isOpened():
                self.index = index
                return True
        
        return False

    def get_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        
        return None

    def close_camera(self):
        if self.cap.isOpened():
            self.cap.release()
