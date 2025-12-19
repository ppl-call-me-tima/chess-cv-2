import pygame
import chess
import math

from helpers.engine_analysis.constants import *

def draw_eval_bar(surface, score, is_mate, winning):
    total_bar_height = SCREEN_HEIGHT - 30
    bar_x = SCREEN_WIDTH - BAR_WIDTH - 30

    if is_mate:
        white_height = 0 if winning == chess.BLACK else total_bar_height
    else:
        # Use logistic function for smooth scaling
        k = 0.004
        white_proportion = 1 / (1 + math.exp(-k * score))
        white_height = int(total_bar_height * white_proportion)
    
    black_height = total_bar_height - white_height

    black_rect = pygame.Rect(bar_x, 10, BAR_WIDTH, black_height)
    white_rect = pygame.Rect(bar_x, 10 + black_height, BAR_WIDTH, white_height)

    pygame.draw.rect(surface, BLACK_COLOR, black_rect)
    pygame.draw.rect(surface, WHITE_COLOR, white_rect)
    
    # --- Draw the score text ---
    text_x = (bar_x + (bar_x + BAR_WIDTH)) // 2
    font = pygame.font.SysFont('Arial', 18, bold=True)
    score_text = ""
    if is_mate:
        mate_in_moves = abs(score)
        score_text = f"MATE #{mate_in_moves}"
        
        if score == 0:
            score_text = "1 - 0" if winning == chess.WHITE else "0 - 1"
    else:
        score_text = f"{score / 100.0:+.2f}"

    if score > 0:
        text_surface = font.render(score_text, True, BLACK_COLOR)
        text_rect = text_surface.get_rect(center=(text_x, SCREEN_HEIGHT - 30))
    elif score < 0:
        text_surface = font.render(score_text, True, WHITE_COLOR)
        text_rect = text_surface.get_rect(center=(text_x, 25))
    else:
        text_color = WHITE_COLOR if winning == chess.BLACK else BLACK_COLOR    
        text_surface = font.render(score_text, True, text_color)
        text_rect = text_surface.get_rect(center=(text_x, SCREEN_HEIGHT / 2))

    surface.blit(text_surface, text_rect)
