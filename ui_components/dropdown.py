import pygame
from typing import List

class Dropdown:
    def __init__(
            self, x, y, width, height, font,
            options: List[str],
            options_indices=None,
            default_text: str="Choose option",
            default_index=None,
            option_height=30,
            bg_colour=(50, 50, 50),
            text_colour=(255, 255, 255),
            hover_colour=(70, 70, 100),
            border_colour=(100, 100, 100),
        ):
        self.rect = pygame.Rect(x, y, width, height)
        self.default_text = default_text
        self.font = font
        self.options = options
        self.options_indices = options_indices
        self.selected_index = default_index
        self.is_open = False
        self.font = font
        self.option_width = self.rect.width
        self.option_height = option_height
        self.bg_colour = bg_colour
        self.text_colour = text_colour
        self.hover_colour = hover_colour
        self.border_colour = border_colour

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.is_open:
                    for i in range(len(self.options)):
                        option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, self.option_width, self.option_height)
                        if option_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.is_open = False
                            return self.options_indices[i] if self.options_indices is not None else i
                    
                    # blank click outside
                    self.is_open = False

                elif self.rect.collidepoint(event.pos):
                    self.is_open = not self.is_open
        
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_colour, self.rect)
        pygame.draw.rect(surface, self.border_colour, self.rect, 1)

        if self.selected_index is not None and 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
        else:
            text = self.default_text
        
        text_surf = self.font.render(text, True, self.text_colour)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)

        arrow_corners = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5),
        ]
        pygame.draw.polygon(surface, self.text_colour, arrow_corners)

        if self.is_open:
            mouse_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, self.option_width, self.option_height)
                colour = self.hover_colour if option_rect.collidepoint(mouse_pos) else self.bg_colour
                pygame.draw.rect(surface, colour, option_rect)
                pygame.draw.rect(surface, self.border_colour, option_rect, 1)

                option_text = self.font.render(option, True, self.text_colour)
                option_rect = option_text.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                surface.blit(option_text, option_rect)
