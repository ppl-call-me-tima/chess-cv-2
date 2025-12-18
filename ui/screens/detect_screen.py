import os
import pygame

from ui.screens.base_screen import BaseScreen
from detection_manager import DetectionManger
from helpers.misc import cv2pygame

class DetectScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 36)
        self.buttons = [
            {"img": "back.png", "action": "back", "rect": pygame.Rect(10, 10, 50, 50)},
            {"img": "tick.png", "action": "set_position_state", "rect": pygame.Rect(70, 10, 50, 50)}
        ]

        self.detection_manager = DetectionManger()

        self.board_rect = pygame.Rect(10, 410, 300, 300)
        self.feed_rect = pygame.Rect(320, 10, 850, 700)
        
        self.board_surf = None
        self.feed_surf = None

    def on_enter(self):
        self.detection_manager.set_position_initial_state(False)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["action"] == "back":
                            self.manager.set_screen("menu")
                        elif btn["action"] == "set_position_state":
                            self.detection_manager.set_position_initial_state(True)

    def update(self):
        self.detection_manager.make_detection()
        
        svg_board = cv2pygame(self.detection_manager.get_board())
        self.board_surf = pygame.surfarray.make_surface(svg_board)

        feed_image = cv2pygame(self.detection_manager.get_feed())
        self.feed_surf = pygame.surfarray.make_surface(feed_image)
        self.feed_surf = pygame.transform.scale(self.feed_surf, (self.feed_rect.width, self.feed_rect.height))

    def draw(self, surface):
        pygame.draw.rect(surface, (20, 20, 20), self.board_rect)
        pygame.draw.rect(surface, (20, 20, 20), self.feed_rect)

        if self.board_surf:
            surface.blit(self.board_surf, self.board_rect)

        if self.feed_surf:
            surface.blit(self.feed_surf, self.feed_rect)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            color = (100, 100, 255) if btn["rect"].collidepoint(mouse_pos) else (70, 70, 70)
            pygame.draw.rect(surface, color, btn["rect"], border_radius=10)
            img = pygame.image.load(os.path.join(f"ui/assets/{btn['img']}"))
            img = pygame.transform.scale(img, (30, 30))
            img_rect = img.get_rect()
            img_rect.center = btn["rect"].center
            surface.blit(img, img_rect)
