import cv2
import chess
import chess.svg
import cairosvg
import io
from PIL import Image
import numpy as np

class Position:
    def __init__(self):
        self.chess = chess.Board()
        self.initial_set = False
        self.current_matrix = []
    
    def clear(self):
        self.chess.clear_board()
        self.initial_set = False
        self.current_matrix = []

    def generate_matrix_with_fen(self, fen):
        current_matrix = []
        fen = fen.split("/")     
        
        i = 0
        
        while i < 8:
            j = 0
            row = []
            
            while j < len(fen[i]):
                if not fen[i][j].isnumeric():
                    row.append(fen[i][j].upper())
                else:
                    cnt = int(fen[i][j])
                    while j < 8 and cnt > 0:
                        row.append("")
                        cnt -= 1
                    
                j += 1
            
            current_matrix.append(row)
            i += 1
        
        return current_matrix

    def compare_and_get_uci(self, m2):
        move_made_from = ""
        move_made_to = ""
        changes = 0
        
        m1 = self.current_matrix
        
        for i in range(8):
            for j in range(8):
                if bool(m1[i][j]) ^ bool(m2[i][j]):
                    if changes > 2:
                        return None
                    else:
                        changes += 1
                        if m1[i][j]:
                            move_made_from = chr(ord("a") + j) + str(8 - i)
                        elif m2[i][j]:
                            move_made_to = chr(ord("a") + j) + str(8 - i)
        
        return move_made_from + move_made_to
                    
    def set_fen(self, FEN):
        self.chess.set_board_fen(FEN)
        self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
        
    def is_initial_set(self):
        return self.initial_set

    def set_initial(self, status):
        self.initial_set = status

    def is_valid(self):      
        # return chess.Board.is_valid(chess.Board(self.current_FEN))
        return self.chess.is_valid()

    def is_next_position_valid(self, next_FEN):
        "Evaluates whether the new receieved position is achievable from self.chess, and push move in stack if True"
        
        valid_position = chess.Board.is_valid(chess.Board(next_FEN))
        
        next_matrix = self.generate_matrix_with_fen(next_FEN)
        uci = self.compare_and_get_uci(next_matrix)
                
        if uci is None:
            achievable_from_current = False
        elif uci == "":
            achievable_from_current = True
        else:
            try:
                self.chess.push_uci(uci)
                achievable_from_current = True
                self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
            except ValueError:
                achievable_from_current = False

        valid = valid_position and achievable_from_current
        
        return valid

    def get_board(self) -> np.ndarray:
        chessboard = self.chess
        svg_string = chess.svg.board(chessboard)
        
        png_data = cairosvg.svg2png(bytestring=svg_string)
        img_pil = Image.open(io.BytesIO(png_data))
        img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_np
