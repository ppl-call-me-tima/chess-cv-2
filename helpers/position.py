import cv2
import asyncio

import chess
import chess.engine

import chess.svg
import cairosvg
import io
from PIL import Image
import numpy as np

from helpers.logger import log
from helpers.engine_analysis.engine_analysis import engine_analysis

class Position:
    def __init__(self):
        self.chess = chess.Board()
        self.initial_set = False
        self.current_matrix = []
        self.board_flipped = False
        self.engine_on = False
        self.engine = None
        self.engine_task: asyncio.Task = None

    async def init_engine(self):
        _, self.engine = await chess.engine.popen_uci(r"stockfish\stockfish-windows-x86-64-avx2.exe")

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

    def set_initial(self, status: bool):
        """
        Set True or False, to lock the continuous change in position. Once True, 
        then position can only be changed via `is_next_position_valid(self, next_FEN)`.
        
        NOTE: it is used only as in implementation indicator flag in main to check
        whether to directly manipulate self.position.fen or do it by trying to add moves onto the move-stack.
        
        :param status: indicator of starting position has been finalized or not
        """
        self.initial_set = status

    def is_valid(self):
        return self.chess.is_valid()

    def is_next_position_valid(self, next_FEN):
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
                
                # log(f"Half move made: {uci}")

                if self.engine_on:
                    if not self.engine_task.done():
                        self.engine_task.cancel()

                    self.engine_task = asyncio.create_task(engine_analysis(self.engine, self.chess))

                new_move_pushed = uci
                achievable_from_current = True
                self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
            except ValueError:
                achievable_from_current = False
        
        return achievable_from_current, new_move_pushed, turn

    async def toggle_engine(self):
        """
        Toggle engine ON/OFF by adding/removing tasks for the engine.
        This function also initializes the engine if it hasn't been yet. Hence needs to be awaited.
        Only works if the initial position is set.
        """
        if not self.initial_set:
            return

        if self.engine is None:
            await self.init_engine()

        if not self.engine_on:
            self.engine_task = asyncio.create_task(engine_analysis(self.engine, self.chess))
        else:
            if not self.engine_task.done():
                self.engine_task.cancel()

        self.engine_on = not self.engine_on

    def undo_move(self):
        try:
            self.chess.pop()
            self.current_matrix = self.generate_matrix_with_fen(self.chess.board_fen())
        except IndexError:
            log("Exception: No moves left to undo.")

    def get_board(self) -> np.ndarray:
        chessboard = self.chess
        svg_string = chess.svg.board(chessboard, size=300, flipped=self.board_flipped)
        
        png_data = cairosvg.svg2png(bytestring=svg_string)
        img_pil = Image.open(io.BytesIO(png_data))
        img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_np

    def flip_board(self):
        self.board_flipped = not self.board_flipped

    async def engine_quit(self):
        if self.engine:
            await self.engine.quit()

    def set_colour_to_play(self, colour: chess.Color):
            self.chess.turn = colour
