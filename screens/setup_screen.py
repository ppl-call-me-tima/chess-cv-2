import os
import pygame

from managers.camera_manager import CameraManager
from managers.inference_manager import InferenceManager
from managers.data_manager import DataManager
from managers.lichess_manager import LichessManager

from screens.base_screen import BaseScreen
from ui_components.dropdown import Dropdown
from helpers.misc import cv2pygame

class SetupScreen(BaseScreen):
    def __init__(self, screen_manager, camera_manager: CameraManager, inference_manager: InferenceManager, data_manager: DataManager, lichess_manager: LichessManager):
        super().__init__(screen_manager)
        self.font = pygame.font.SysFont("Arial", 25)
        self.font_colour = pygame.Color(255, 255, 255)

        self.buttons = [
            {"img": "back.png", "action": "back", "active": True, "rect": pygame.Rect(10, 10, 50, 50)},
            {"text": "Paste Lichess Token", "action": "lichess_token", "active": True, "rect": pygame.Rect(50, 600, 400, 40)}
        ]
        
        self.camera_manager = camera_manager
        self.inference_manager = inference_manager
        self.data_manager = data_manager
        self.lichess_manager = lichess_manager

        self.cameras = self.camera_manager.get_camera_list()
        self.devices = self.inference_manager.get_device_list()

        self.labels = [
            {"text": "Select Camera:", "rect": pygame.Rect(50, 170, 400, 30)},
            {"text": "Select GPU/CPU:", "rect": pygame.Rect(50, 370, 400, 30)},
            {"text": "Verify username:", "rect": pygame.Rect(50, 570, 200, 30)},
        ]

        self.camera_dropdown = Dropdown(
            50, 200, 400, 40,
            label="camera_index",
            font=self.font,
            options=[cam[1] for cam in self.cameras], 
            default_text="Choose camera"
        )
        self.gpu_dropdown = Dropdown(
            50, 400, 400, 40,
            label="inference_index",
            font=self.font,
            options=self.devices,
            default_text="Choose inference device",
        )

        self.feed_surf = None
        self.feed_rect = pygame.Rect(500, 50, 730, 620)
        self.feed_text = "No camera selected"

        self.username_rect = pygame.Rect(210, 570, 200, 30)
        self.username_text = None

    def on_enter(self):
        self.data_manager.read_and_update_managers()

    async def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["action"] == "back":
                            self.screen_manager.set_screen("menu")
                        elif btn["action"] == "lichess_token":
                            token = pygame.scrap.get(pygame.SCRAP_TEXT).decode().rstrip('\x00')
                            self.data_manager.set_value(token, "lichess_token")
                            self.username_text = self.lichess_manager.set_token(token)

        camera_index = self.camera_dropdown.handle_event(event, self.data_manager)
        gpu_index = self.gpu_dropdown.handle_event(event, self.data_manager)

        if camera_index is not None:
            self.camera_manager.set_camera(camera_index)
        if gpu_index is not None:
            self.inference_manager.set_device(gpu_index)

    def update(self):
        if self.camera_manager.cap is None:
            return

        frame = cv2pygame(self.camera_manager.get_frame())
        if frame is not None:
            self.feed_surf = pygame.surfarray.make_surface(frame)
            self.feed_surf = pygame.transform.scale(self.feed_surf, (self.feed_rect.width, self.feed_rect.height))
        else:
            self.feed_surf = None
            self.feed_text = "Camera not available"

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
                if not btn["active"]: continue

                color = (100, 100, 255) if btn["rect"].collidepoint(mouse_pos) else (70, 70, 70)

                if "img" in btn:
                    pygame.draw.rect(surface, color, btn["rect"], border_radius=10)
                    img = pygame.image.load(os.path.join(f"assets/{btn['img']}"))
                    img = pygame.transform.scale(img, (40, 40))
                    img_rect = img.get_rect(center=btn["rect"].center)
                    surface.blit(img, img_rect)
                elif "text" in btn:
                    pygame.draw.rect(surface, color, btn["rect"], border_radius=10)
                    text_surf = self.font.render(btn["text"], True, (255, 255, 255))
                    text_rect = text_surf.get_rect(center=btn["rect"].center)
                    surface.blit(text_surf, text_rect)

        for label in self.labels:
            surface.blit(self.font.render(label["text"], True, self.font_colour), label["rect"])
        
        self.camera_dropdown.draw(surface)
        self.gpu_dropdown.draw(surface)

        pygame.draw.rect(surface, (255, 255, 255), self.feed_rect, 1)

        if self.feed_surf:
            surface.blit(self.feed_surf, self.feed_rect)
        else:
            text_surf = self.font.render(self.feed_text, True, (100, 100, 100))
            text_rect = text_surf.get_rect(center=self.feed_rect.center)
            surface.blit(text_surf, text_rect)

        pygame.draw.rect(surface, (10, 10, 10), self.username_rect)
        if self.username_text:
            text_surf = self.font.render(self.username_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.username_rect.center)
            surface.blit(text_surf, text_rect)
