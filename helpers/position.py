import cv2
import chess
import chess.svg
import cairosvg
import io
from PIL import Image
import numpy as np
from logger import log

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
                    row.append(fen[i][j])
                else:
                    cnt = int(fen[i][j])
                    while j < 8 and cnt > 0:
                        row.append("")
                        cnt -= 1
                    
                j += 1
            
            current_matrix.append(row)
            i += 1
        
        return current_matrix

    def get_uci(self, square):
        i,j = square
        return chr(ord("a") + j) + str(8 - i)

    def compare_and_get_uci(self, m2):
        move_made_from = ""
        move_made_to = ""
        promoted_to = ""
        changed_squares = []
        
        m1 = self.current_matrix
        
        for i in range(8):
            for j in range(8):
                if m1[i][j] != m2[i][j]:
                    changed_squares.append((i,j))        

        if len(changed_squares) == 0:
            return ""
        
        if len(changed_squares) == 1:
            return None

        if len(changed_squares) > 2:
            return None
            # TODO: special moves - castling + en-passant
        
        s1, s2 = changed_squares
        
        # checking for pawn promotion
        if (m1[s1[0]][s1[1]] == "P" and s1[0] == 1 and s2[0] == 0 and m2[s2[0]][s2[1]] != "") or (m1[s1[0]][s1[1]] == "p" and s1[0] == 6 and s2[0] == 7 and m2[s2[0]][s2[1]] != ""):
            promoted_to = m2[s2[0]][s2[1]].lower()
            move_made_from = self.get_uci(s1)
            move_made_to = self.get_uci(s2)
        elif (m1[s2[0]][s2[1]] == "P" and s2[0] == 1 and s1[0] == 0 and m2[s1[0]][s1[1]] != "") or (m1[s2[0]][s2[1]] == "p" and s2[0] == 6 and s1[0] == 7 and m2[s1[0]][s1[1]] != ""):
            promoted_to = m2[s1[0]][s1[1]].lower()
            move_made_from = self.get_uci(s2)
            move_made_to = self.get_uci(s1)
        
        # basic move
        elif (m1[s1[0]][s1[1]] == "") ^ (m1[s2[0]][s2[1]] == ""):
            if m1[s1[0]][s1[1]]:
                move_made_from = self.get_uci(s1)
                move_made_to = self.get_uci(s2)
            else:
                move_made_from = self.get_uci(s2)
                move_made_to = self.get_uci(s1)
        
        # capture
        elif m1[s1[0]][s1[1]] and m1[s2[0]][s2[1]]:
            if m1[s1[0]][s1[1]] == m2[s2[0]][s2[1]] and m2[s1[0]][s1[1]] == "":
                move_made_from = self.get_uci(s1)
                move_made_to = self.get_uci(s2)
            elif m1[s2[0]][s2[1]] == m2[s1[0]][s1[1]] and m2[s2[0]][s2[1]] == "":
                move_made_from = self.get_uci(s2)
                move_made_to = self.get_uci(s1)
        
        # unrecognised move
        else:
            return None
        
        # for touching pawn on last rank to not be detected
        if promoted_to == "p":
            return None
        
        return move_made_from + move_made_to + promoted_to
                    
    def set_fen(self, FEN, castling_fen):
        self.chess.set_fen(FEN)
        self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
        self.chess.set_castling_fen(castling_fen)
        
    def is_initial_set(self):
        return self.initial_set

    def set_initial(self, status):
        self.initial_set = status

    def is_valid(self):
        return self.chess.is_valid()

    def is_next_position_valid(self, next_FEN):
        "Evaluates whether the new receieved position is achievable from self.chess, and push move in stack if True"
        
        # valid_position = chess.Board.is_valid(chess.Board(next_FEN))
        
        next_matrix = self.generate_matrix_with_fen(next_FEN)
        uci = self.compare_and_get_uci(next_matrix)
        new_move_pushed = None
        turn = self.chess.turn

        if uci is None:
            achievable_from_current = False
        elif uci == "":
            achievable_from_current = True
        else:
            try:
                self.chess.push_uci(uci)
                new_move_pushed = uci
                achievable_from_current = True
                self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
            except ValueError:
                achievable_from_current = False
        
        return achievable_from_current, new_move_pushed, turn

    def get_board(self) -> np.ndarray:
        chessboard = self.chess
        svg_string = chess.svg.board(chessboard)
        
        png_data = cairosvg.svg2png(bytestring=svg_string)
        img_pil = Image.open(io.BytesIO(png_data))
        img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_np
