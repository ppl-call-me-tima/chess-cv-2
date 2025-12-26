import cpuinfo
import torch

class InferenceManager:
    def __init__(self):
        self.device = None
        self.device_list = []

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
