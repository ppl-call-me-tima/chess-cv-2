import os
import pygame
from chess import WHITE, BLACK

from screens.base_screen import BaseScreen

from managers.detection_manager import DetectionManger
from managers.lichess_manager import LichessManager
from managers.data_manager import DataManager

from helpers.misc import cv2pygame
from helpers.engine_analysis.shared_resource import shared_resource
from helpers.engine_analysis.eval_bar import draw_eval_bar

class DetectScreen(BaseScreen):
    def __init__(self, screen_manager, camera_manager, inference_manager, data_manager: DataManager, lichess_manager: LichessManager):
        super().__init__(screen_manager)

        self.board_rect = pygame.Rect(10, 410, 300, 300)
        self.feed_rect = pygame.Rect(320, 10, 850, 700)

        self.board_surf = None
        self.feed_surf = None

        self.detection_manager = DetectionManger(camera_manager, inference_manager)
        self.lichess_manager = lichess_manager
        self.data_manager = data_manager

        self.font = pygame.font.SysFont("Arial", 24)
        self.buttons = [
            {"img": "back.png", "action": "back", "active": True,                     "rect": pygame.Rect(10, 10, 50, 50)},
            {"img": "white_king.png", "action": "set_position_state", "active": True, "rect": pygame.Rect(70, 10, 50, 50)},
            {"img": "black_king.png", "action": "set_position_state", "active": True, "rect": pygame.Rect(130, 10, 50, 50)},
            {"img": "cross.png", "action": "reset_position_state", "active": False,   "rect": pygame.Rect(190, 10, 50, 50)},
            {"img": "undo.png", "action": "undo", "active": False,                    "rect": pygame.Rect(250, 10, 50, 50)},

            {"text": "Connect LICHESS", "action": "connect_lichess", "active": True, "rect": pygame.Rect(10, 350, 300, 50)},
            {"text": "ENGINE", "action": "engine_on", "active": True,                "rect": pygame.Rect(1175, 350, 100, 50)},
            {"action": "engine_off", "active": False,                                "rect": pygame.Rect(1200, 10, 50, 690)},
            {"action": "flip_board", "active": True,                                 "rect": self.board_rect}
        ]

    def on_enter(self):
        self.detection_manager.position.set_initial(False)
        self.data_manager.read_and_update_managers()

    async def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos) and btn["active"]:
                        if btn["action"] == "back":
                            self.screen_manager.set_screen("menu")
                        elif btn["action"] == "set_position_state":
                            self.detection_manager.position.set_initial(True)

                            if btn["img"] == "white_king.png":
                                self.detection_manager.position.set_colour_to_play(WHITE)
                            elif btn["img"] == "black_king.png":
                                self.detection_manager.position.set_colour_to_play(BLACK)

                        elif btn["action"] == "reset_position_state":
                            self.detection_manager.position.set_initial(False)
                        elif btn["action"] == "undo":
                            self.detection_manager.position.undo_move()
                        elif btn["action"] == "connect_lichess":
                            self.lichess_manager.set_credentials()
                        elif btn["action"] == "engine_on" or btn["action"] == "engine_off":
                            await self.detection_manager.position.toggle_engine()
                        elif btn["action"] == "flip_board":
                            self.detection_manager.position.flip_board()

    def update(self):
        self.detection_manager.make_detection(self.lichess_manager)

        for btn in self.buttons:
            if self.detection_manager.position.is_initial_set():
                if btn["action"] == "set_position_state":
                    btn["active"] = False
                elif btn["action"] == "reset_position_state" or btn["action"] == "undo":
                    btn["active"] = True
            else:
                if btn["action"] == "set_position_state":
                    btn["active"] = True
                elif btn["action"] == "reset_position_state" or btn["action"] == "undo":
                    btn["active"] = False

        # TODO: find some better way to do this
        if self.lichess_manager.is_lichess_connected():
            self.buttons[5]["active"] = False
        else:
            self.buttons[5]["active"] = True
        
        if self.detection_manager.position.engine_on:
            self.buttons[6]["active"] = False
            self.buttons[7]["active"] = True
        else:
            self.buttons[6]["active"] = True
            self.buttons[7]["active"] = False

        svg_board = cv2pygame(self.detection_manager.position.get_board())
        self.board_surf = pygame.surfarray.make_surface(svg_board)

        frame = self.detection_manager.get_feed()
        if frame is None:
            return

        feed_image = cv2pygame(frame)
        self.feed_surf = pygame.surfarray.make_surface(feed_image)
        self.feed_surf = pygame.transform.scale(self.feed_surf, (self.feed_rect.width, self.feed_rect.height))

    def draw(self, surface):
        pygame.draw.rect(surface, (20, 20, 20), self.board_rect)
        pygame.draw.rect(surface, (100, 100, 100), self.board_rect, 1)

        pygame.draw.rect(surface, (20, 20, 20), self.feed_rect)
        pygame.draw.rect(surface, (100, 100, 100), self.feed_rect, 1)

        if self.board_surf:
            surface.blit(self.board_surf, self.board_rect)

        if self.feed_surf:
            surface.blit(self.feed_surf, self.feed_rect)
        else:
            text_surf = self.font.render("Camera feed not available", True, (100, 100, 100))
            text_rect = text_surf.get_rect(center=self.feed_rect.center)
            surface.blit(text_surf, text_rect)

        if self.detection_manager.position.engine_on:
            draw_eval_bar(
                surface,
                shared_resource["score"],
                shared_resource["is_mate"],
                shared_resource["winning"]
            )

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
            else:
                pass
