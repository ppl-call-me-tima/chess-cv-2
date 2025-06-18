import os
import cv2

import chess
import chess.svg
import cairosvg
import io
from PIL import Image
import numpy as np

class Chessboard:
    def __init__(self, xy, piece_class, N):
        self.matrix = []
        
        PADDING = int(os.environ.get("BOARD_PADDING"))
        DELTA = int(os.environ.get("SQUARE_DIMENSION"))
        END = N - PADDING - DELTA + 1
        
        for y in range(PADDING, END, DELTA):
            row = []
            
            for x in range(PADDING, END, DELTA):
                x_end = x + DELTA
                y_end = y + DELTA

                for i in range(len(xy)):
                    cood = xy[i]
                    if cood[0] >= x and cood[0] <= x_end and cood[1] >= y and cood[1] <= y_end:
                        row.append(self.symbol(piece_class[i]))
                        break
                else:
                    row.append("")

            self.matrix.append(row)
    
    def symbol(class_name):
        if (class_name[5:] == "Knight"):
            symbol = "N"
        else:
            symbol = class_name[5]
        
        if class_name[:5] == "Black":
            symbol = symbol.lower()
        
        return symbol
    
    def FEN(self):
        fen = ""

        for row in self.matrix:
            empty = 0

            for symbol in row:
                if symbol == "":
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += symbol
            else:
                if empty > 0:
                    fen += str(empty)
                fen += "/"

        fen = fen[:-1]
        return fen

    def chessboard(self) -> np.ndarray:
        chessboard = chess.Board(fen=self.FEN())
        svg_string = chess.svg.board(chessboard)
        
        png_data = cairosvg.svg2png(bytestring=svg_string)
        img_pil = Image.open(io.BytesIO(png_data))
        img_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_np
