import pygame

PIECES_SPRITE_SHEET_PATH = r"assets\chesspieces.png"

class VirtualBoard:
    def __init__(self):
        self.is_enabled = True
        self.matrix = [[""] * 8 for i in range(8)]  # 8x8 matrix respresenting board
        self.state_matrix = {}                      # dict of {cood: pygame.Rect}
        self.held_piece_cood = None                 # (r, c) of chessboard sq of piece held / None

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for cood, rect in self.state_matrix.items():
                mouse_pos = event.pos
                if rect.collidepoint(mouse_pos):
                    if self.held_piece_cood is None:
                        self.held_piece_cood = cood
                    else:
                        r, c = self.held_piece_cood
                        piece = self.matrix[r][c]
                        
                        self.matrix[r][c] = ""
                        self.matrix[cood[0]][cood[1]] = piece
                        self.held_piece_cood = None

    def __load_sprite_sheet(self, SQ_SIZE):
        sheet = pygame.image.load(PIECES_SPRITE_SHEET_PATH).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        piece_width = sheet_width // 6
        piece_height = sheet_height // 2

        piece_map = {
            "K": (0, 0), "Q": (1, 0), "B": (2, 0), "N": (3, 0), "R": (4, 0), "P": (5, 0),
            "k": (0, 1), "q": (1, 1), "b": (2, 1), "n": (3, 1), "r": (4, 1), "p": (5, 1),
        }

        images = {}

        for name, pos in piece_map.items():
            rect = pygame.Rect(pos[0] * piece_width, pos[1] * piece_height, piece_width, piece_height)
            piece_image = sheet.subsurface(rect)
            images[name] = pygame.transform.scale(piece_image, (SQ_SIZE, SQ_SIZE))
        
        return images

    def draw_board(self, surface: pygame.Surface, board_rect: pygame.Rect):
        # board
        HEIGHT = board_rect.height
        DIMENSION = 8
        SQ_SIZE = HEIGHT // DIMENSION

        piece_images = self.__load_sprite_sheet(SQ_SIZE)

        for r in range(DIMENSION):
            for c in range(DIMENSION):
                colour = (50, 50, 50) if (r + c) % 2 else (245, 245, 245)
                x = board_rect.left + c * SQ_SIZE + 1
                y = board_rect.top + r * SQ_SIZE + 1
                rect = pygame.Rect(x, y, SQ_SIZE, SQ_SIZE)
                self.state_matrix[(r, c)] = rect
                pygame.draw.rect(surface, colour, rect)

                if self.matrix[r][c] != "":
                    surface.blit(piece_images[self.matrix[r][c]], (x, y))

        # piece selection
