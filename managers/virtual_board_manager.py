import pygame

PIECES_SPRITE_SHEET_PATH = r"assets\chesspieces.png"

class VirtualBoard:
    def __init__(self, feed_rect: pygame.Rect):
        self.is_enabled = True

        self.LEFT = feed_rect.left
        self.TOP = feed_rect.top
        self.HEIGHT = feed_rect.height
        self.SQ_SIZE = feed_rect.height // 8
        self.SELECTOR_SQ_SIZE = int(0.75 * self.SQ_SIZE)

        self.board_matrix = [[""] * 8 for i in range(8)]         # 8x8 matrix respresenting board
        self.board_state_matrix = {}                             # dict of {cood: pygame.Rect} for chessboard
        self.selector_state_matrix = {}                          # dict of {piece: pygame.Rect} for selector pallette
        self.held_piece = {"piece": None, "is_infinite": False}

        self.selector_matrix = (
            ("K", "Q", "B", "N", "R", "P"),
            ("k", "q", "b", "n", "r", "p"),
        )

        self.piece_images, self.selector_images = self.__load_sprite_sheet()  # dict of {piece: pygame.Surface (piece/selector image)}

    def __load_sprite_sheet(self):
        sheet = pygame.image.load(PIECES_SPRITE_SHEET_PATH).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        piece_width = sheet_width // 6
        piece_height = sheet_height // 2

        piece_map = {
            "K": (0, 0), "Q": (1, 0), "B": (2, 0), "N": (3, 0), "R": (4, 0), "P": (5, 0),
            "k": (0, 1), "q": (1, 1), "b": (2, 1), "n": (3, 1), "r": (4, 1), "p": (5, 1),
        }

        piece_images = {}
        selector_images = {}

        for name, pos in piece_map.items():
            rect = pygame.Rect(pos[0] * piece_width, pos[1] * piece_height, piece_width, piece_height)
            piece_image = sheet.subsurface(rect)
            piece_images[name] = pygame.transform.scale(piece_image, (self.SQ_SIZE, self.SQ_SIZE))
            selector_images[name] = pygame.transform.scale(piece_image, (self.SELECTOR_SQ_SIZE, self.SELECTOR_SQ_SIZE))

        return piece_images, selector_images

    def handle_event(self, event: pygame.event.Event):
        # move making and infinite piece selecting
        if event.type == pygame.MOUSEBUTTONDOWN:
            for cood, rect in self.board_state_matrix.items():
                mouse_pos = event.pos
                if rect.collidepoint(mouse_pos):
                    if self.held_piece["piece"] is None and not self.held_piece["is_infinite"]:
                        if self.board_matrix[cood[0]][cood[1]] != "":
                            self.held_piece["piece"] = self.board_matrix[cood[0]][cood[1]]
                            self.board_matrix[cood[0]][cood[1]] = ""
                    else:
                        self.board_matrix[cood[0]][cood[1]] = self.held_piece["piece"]
                        self.held_piece["piece"] = None
                        self.held_piece["is_infinite"] = False

            for piece, rect in self.selector_state_matrix.items():
                mouse_pos = event.pos
                if rect.collidepoint(mouse_pos):
                    self.held_piece["piece"] = piece
                    self.held_piece["is_infinite"] = True

    def draw_board(self, surface: pygame.Surface):
        # board
        for r in range(8):
            for c in range(8):
                colour = (60, 60, 60) if (r + c) % 2 else (245, 245, 245)
                x = self.LEFT + c * self.SQ_SIZE + 1
                y = self.TOP + r * self.SQ_SIZE + 1
                rect = pygame.Rect(x, y, self.SQ_SIZE, self.SQ_SIZE)
                self.board_state_matrix[(r, c)] = rect
                pygame.draw.rect(surface, colour, rect)

                if self.board_matrix[r][c] != "":
                    surface.blit(self.piece_images[self.board_matrix[r][c]], (x, y))

        # sq highlighting
        mouse_pos = pygame.mouse.get_pos()
        for rect in self.board_state_matrix.values():
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (255, 0, 0), rect, 2)

        # infinite piece selector pallette
        for c in range(2):
            for r in range(6):
                x = self.LEFT + self.HEIGHT + c * self.SELECTOR_SQ_SIZE
                y = self.TOP + r * self.SELECTOR_SQ_SIZE
                rect = pygame.Rect(x, y, self.SELECTOR_SQ_SIZE, self.SELECTOR_SQ_SIZE)
                self.selector_state_matrix[self.selector_matrix[c][r]] = rect
                surface.blit(self.selector_images[self.selector_matrix[c][r]], (x, y))
