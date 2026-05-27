import os
import pygame

from managers.camera_manager import CameraManager
from managers.inference_manager import InferenceManager
from managers.data_manager import DataManager
from managers.lichess_manager import LichessManager
from managers.virtual_board_manager import VirtualBoardManager

from screens.base_screen import BaseScreen
from ui_components.dropdown import Dropdown
from helpers.misc import cv2pygame

class SetupScreen(BaseScreen):
    def __init__(
            self, screen_manager,
            camera_manager: CameraManager,
            inference_manager: InferenceManager,
            data_manager: DataManager,
            lichess_manager: LichessManager,
            virtual_board_manager: VirtualBoardManager,
        ):

        super().__init__(screen_manager)
        self.font = pygame.font.SysFont("Arial", 25)
        self.font_colour = pygame.Color(255, 255, 255)

        self.buttons = [
            {"img": "back.png", "action": "back", "active": True, "rect": pygame.Rect(10, 10, 50, 50)},
            {"text": "Paste Lichess Token", "action": "lichess_token", "active": True, "rect": pygame.Rect(50, 490, 400, 40)},
            {"text": "ON", "action": "virtual_on", "active": True, "rect": pygame.Rect(250, 625, 60, 40)},
            {"text": "OFF", "action": "virtual_off", "active": True, "rect": pygame.Rect(330, 625, 60, 40)},
        ]
        
        self.camera_manager = camera_manager
        self.inference_manager = inference_manager
        self.data_manager = data_manager
        self.lichess_manager = lichess_manager
        self.virtual_board_manager = virtual_board_manager

        self.cameras = self.camera_manager.get_camera_list()
        self.devices = self.inference_manager.get_device_list()

        # labels
        starting_y = 100
        gap_y = 175

        self.labels = [
            {"text": "Select Camera:"},
            {"text": "Select GPU/CPU:"},
            {"text": "Verify username:"},
            {"text": "Virtual Keyboard:"},
        ]

        for idx, label in enumerate(self.labels):
            label["rect"] = pygame.Rect(50, starting_y + idx * gap_y, 200, 30)

        # dropdowns
        label_dropdown_gap_y = 30
        
        self.dropdowns = [
            Dropdown(
                50, 0, 400, 40,
                label="camera_index",
                font=self.font,
                options=[cam[1] for cam in self.cameras],
                default_text="Choose camera"
            ),
            Dropdown(
                50, 0, 400, 40,
                label="inference_index",
                font=self.font,
                options=self.devices,
                default_text="Choose inference device",
            )
        ]

        for i in range(len(self.dropdowns)):
            self.dropdowns[i].rect.y = self.labels[i]["rect"].y + label_dropdown_gap_y

        self.feed_surf = None
        self.feed_rect = pygame.Rect(500, 50, 730, 620)
        self.feed_text = "No camera selected"

        self.username_rect = pygame.Rect(210, 450, 200, 30)
        self.username_text = None

    def on_enter(self):
        self.data_manager.read_and_update_managers()

    def on_exit(self):
        self.camera_manager.close_camera()

    async def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["action"] == "back":
                            self.on_exit()
                            self.screen_manager.set_screen("menu")
                        elif btn["action"] == "lichess_token":
                            token = pygame.scrap.get(pygame.SCRAP_TEXT).decode().rstrip('\x00')
                            username = self.lichess_manager.fetch_username(token)

                            if username:
                                self.data_manager.set_value(token, "lichess_token")
                                self.data_manager.set_value(username, "lichess_username")
                                self.username_text = username
                        elif btn["action"].startswith("virtual"):
                            self.virtual_board_manager.is_enabled = btn["action"].endswith("on")

        camera_index = self.dropdowns[0].handle_event(event, self.data_manager)
        gpu_index = self.dropdowns[1].handle_event(event, self.data_manager)

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

                if btn["action"].startswith("virtual"):
                    if btn["action"].endswith("on") and self.virtual_board_manager.is_enabled or \
                       btn["action"].endswith("off") and not self.virtual_board_manager.is_enabled:
                        color = (100, 100, 255)
                    else:
                        color = (70, 70, 70)
                else:
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
        
        for dropdown in self.dropdowns:
            dropdown.draw(surface)

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
