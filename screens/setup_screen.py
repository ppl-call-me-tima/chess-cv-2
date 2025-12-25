import cv2
from cv2_enumerate_cameras import enumerate_cameras
import pygame

from ui_components.dropdown import Dropdown
from screens.base_screen import BaseScreen

class SetupScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 25)
        self.font_colour = pygame.Color(255, 255, 255)
        
        self.cameras = [(cam.index, cam.name) for cam in enumerate_cameras(cv2.CAP_MSMF)]
        
        self.labels = [
            {"text": "Select Camera:", "rect": pygame.Rect(50, 170, 400, 30)},
            {"text": "Select GPU/CPU:", "rect": pygame.Rect(50, 420, 400, 30)},
        ]

        self.camera_dropdown = Dropdown(
            50, 200, 400, 40,
            font=self.font,
            options=[cam[1] for cam in self.cameras], 
            default_text="Choose camera"
        )
        self.gpu_dropdown = Dropdown(
            50, 450, 400, 40,
            font=self.font,
            options=["CPU", "GPU"],
            default_text="Choose GPU",
        )

        self.feed_surf = None

    async def handle_event(self, event):
        selected_camera_index = self.camera_dropdown.handle_event(event)
        selected_gpu_index = self.gpu_dropdown.handle_event(event)

    def draw(self, surface):
        self.camera_dropdown.draw(surface)
        self.gpu_dropdown.draw(surface)

        for label in self.labels:
            surface.blit(self.font.render(label["text"], True, self.font_colour), label["rect"])
