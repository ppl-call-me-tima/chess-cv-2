import pygame

from ui.screens.base_screen import BaseScreen
from detection_manager import DetectionManger
from helpers.misc import cv2pygame

class DetectScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 36)
        self.detection_manager = DetectionManger()
        self.board_surf = None
        self.board_rect = pygame.Rect(10, 410, 300, 300)
        self.feed_surf = None
        self.feed_rect = pygame.Rect(320, 10, 850, 700)
    
    def update(self, time_delta):
        # using detection manager: a sole function makes inference, and set respective thingies: the svg board; and the bigger board, chessboard
        # that inference function can have its own states such as warped_xy, chessboard, etc. from the original main() vaarisbles
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
