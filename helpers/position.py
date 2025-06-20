import chess

class Position:
    def __init__(self):
        self.initial_set = False
        self.current_FEN = None
        self.current_board = None
    
    def clear(self):
        self.initial_set = False
        self.current_FEN = None
        self.current_board = None

    def set_fen_board(self, FEN, board):
        self.current_FEN = FEN
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
        achievable_from_current = True  # TODO

        valid = valid_position and achievable_from_current

        if valid:
            self.current_FEN = next_FEN
            self.current_board = next_board
        
        return valid
