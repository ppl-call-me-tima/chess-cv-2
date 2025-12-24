import cv2
from cv2_enumerate_cameras import enumerate_cameras
import pygame

from ui_components.dropdown import Dropdown
from screens.base_screen import BaseScreen

class SetupScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 25)
        
        self.cameras = [(cam.index, cam.name) for cam in enumerate_cameras(cv2.CAP_MSMF)]
        self.camera_dropdown = Dropdown(
            10, 10, 300, 40, self.font, 
            options=[cam[1] for cam in self.cameras], 
            default_text="Choose camera"
        )

    async def handle_event(self, event):
        selected_index = self.camera_dropdown.handle_event(event)

    def draw(self, surface):
        self.camera_dropdown.draw(surface)
