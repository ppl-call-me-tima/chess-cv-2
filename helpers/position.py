import chess

class Position:
    def __init__(self):
        self.initial_set = False
        self.current_FEN = None
        self.current_matrix = []
        self.current_board = None
    
    def clear(self):
        self.initial_set = False
        self.current_FEN = None
        self.current_matrix = []
        self.current_board = None

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
        move_made_from = "00"
        move_made_to = "00"
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
                    
    def set_fen_board(self, FEN, board):
        self.current_FEN = FEN
        self.current_matrix = self.generate_matrix_with_fen(self.current_FEN)
        self.current_board = board
        
    def is_initial_set(self):
        return self.initial_set

    def set_initial(self, status):
        self.initial_set = status

    def get_board(self):
        return self.current_board

    def is_valid(self):      
        return chess.Board.is_valid(chess.Board(self.current_FEN))

    def is_next_position_valid(self, next_FEN, next_board):
        "Evaluates whether the new receieved position is achievable from self.current_FEN, and sets as itself if True"
        
        valid_position = chess.Board.is_valid(chess.Board(next_FEN))
        
        next_matrix = self.generate_matrix_with_fen(next_FEN)
        uci = self.compare_and_get_uci(next_matrix)
        
        try:
            chess.Board(self.current_FEN).push_uci(uci)
            achievable_from_current = True
        except ValueError:
            achievable_from_current = False

        valid = valid_position and achievable_from_current

        if valid:
            self.current_FEN = next_FEN
            self.current_board = next_board
        
        return valid
