import pygame
from ui.screens.base_screen import BaseScreen

class MenuScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", 36)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.buttons = [
            {"text": "DETECT", "action": "detect", "rect": pygame.Rect(0, 0, 300, 60)},
            {"text": "EXIT", "action": "exit", "rect": pygame.Rect(0, 0, 300, 60)},
        ]

        mid_x = 1280 / 2
        start_y = 300
        margin_bottom = 80

        for i, btn in enumerate(self.buttons):
            btn["rect"].centerx = mid_x
            btn["rect"].centery = start_y + i * margin_bottom
    
    async def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["action"] == "exit":
                            pygame.event.post(pygame.event.Event(pygame.QUIT))
                        else:
                            self.manager.set_screen(btn["action"])

    def draw(self, surface):
        title_surf = self.title_font.render("chessCV", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(640, 150))
        surface.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            color = (100, 100, 255) if btn["rect"].collidepoint(mouse_pos) else (70, 70, 70)
            pygame.draw.rect(surface, color, btn["rect"], border_radius=10)

            text_surf = self.font.render(btn["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            surface.blit(text_surf, text_rect)
