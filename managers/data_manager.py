import os
import json

from managers.camera_manager import CameraManager
from managers.inference_manager import InferenceManager
from managers.lichess_manager import LichessManager

from helpers.logger import log

class DataManager:
    def __init__(self, camera_manager: CameraManager, inference_manager: InferenceManager, lichess_manager: LichessManager):
        self.file = "settings.json"
        self.camera_manager = camera_manager
        self.inference_manager = inference_manager
        self.lichess_manager = lichess_manager

        if not os.path.exists(self.file):
            with open(self.file, "w"): pass
    
    def get_dict(self):
        try:
            with open(self.file, "r") as f:
                data = f.read()
                if not data:
                    return {}
                return json.loads(data)
        except Exception as e:
            log(e.__str__())
            return {}

    def read_and_update_managers(self):
        file_data = self.get_dict()

        if "camera_index" in file_data:
            self.camera_manager.set_camera(int(file_data.get("camera_index")))
        if "inference_index" in file_data:
            self.inference_manager.set_device(int(file_data.get("inference_index")))
        if "lichess_token" in file_data:
            self.lichess_manager.set_token(file_data.get("lichess_token"))

    def set_value(self, index: int | str, label: str):
        file_data = self.get_dict()
        with open(self.file, "w") as f:
            file_data[label] = index
            f.write(json.dumps(file_data))
