import pygame
from ui.screens.base_screen import BaseScreen

class DetectScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 36)

        self.detections_manager = None

        self.board_surf = None
        self.board_rect = pygame.Rect(10, 490, 200, 200)
    
    def update(self, time_delta):
        # using detection manager: a sole function makes inference, and set respective thingies: the svg board; and the bigger board, chessboard
        # that inference function can have its own states such as warped_xy, chessboard, etc. from the original main() vaarisbles
        
        # getter functions that set surfaces here to build all of that and display on the screen
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, (20, 20, 20), self.board_rect)
