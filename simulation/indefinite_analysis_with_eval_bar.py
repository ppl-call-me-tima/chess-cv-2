import asyncio
import chess
import chess.engine
import random
import pygame
import time
import math

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 600
BAR_WIDTH = 50
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (50, 50, 50)
BACKGROUND_COLOR = (30, 30, 30)

shared_resource = {
    "score": 0,
    "is_mate": False,
    "winning": chess.WHITE,
}

async def engine_analysis(engine: chess.engine.UciProtocol, board: chess.Board):
    with await engine.analysis(board) as analysis:
        async for info in analysis:
            score = info.get("score")
            seldepth = info.get("seldepth", 0)
            is_mate = score.is_mate() if score else None

            if score:
                print(score.white())
                
                if score.is_mate():
                    shared_resource["is_mate"] = True
                    shared_resource["score"] = score.white().mate()
                    
                    if score.white().mate() > 0:
                        shared_resource["winning"] = chess.WHITE
                    elif score.white().mate() < 0:
                        shared_resource["winning"] = chess.BLACK
                else:
                    shared_resource["is_mate"] = False
                    shared_resource["score"] = score.white().score()

            if is_mate or seldepth > 60:
                break

def draw_eval_bar(surface, score, is_mate, winning):
    surface.fill(BACKGROUND_COLOR)
    total_bar_height = SCREEN_HEIGHT - 20
    bar_x = (SCREEN_WIDTH - BAR_WIDTH) / 2

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
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25))
    elif score < 0:
        text_surface = font.render(score_text, True, WHITE_COLOR)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, 25))
    else:
        text_color = WHITE_COLOR if winning == chess.BLACK else BLACK_COLOR    
        text_surface = font.render(score_text, True, text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    surface.blit(text_surface, text_rect)

async def main():
    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
    
    board = chess.Board()
    engine_task = None
    
    transport, engine = await chess.engine.popen_uci(r"C:\Users\2648a\dev\projects\cv\segmentation\stockfish\stockfish-windows-x86-64-avx2.exe")

    next_move_time = time.time()
    running = True
    i = 0
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Async Chess Eval")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
                if engine_task and not engine_task.done():
                    engine_task.cancel()

        # simulate player thinking        
        if i < len(moves) and time.time() >= next_move_time:
            print(f"\nHalf move was made #{i + 1}: {moves[i]}")
            board.push_uci(moves[i])
            
            i += 1
            next_move_time += random.randint(1, 10)
            
            if engine_task and not engine_task.done():
                print("---ABORT ENGINE TASK ---")
                engine_task.cancel()
            
            engine_task = asyncio.create_task(engine_analysis(engine, board))
        
        draw_eval_bar(screen, shared_resource["score"], shared_resource["is_mate"], shared_resource["winning"])
        pygame.display.flip()
        await asyncio.sleep(1/60)
    
    # during the last move analysis, when the main coroutine finished its stuff and only the engine_task is left to complete,
    # since asyncio.run(main()) only cares about the main co-routine's execution, it starts killing all main's generated
    # tasks as well. we need to await it manually after main is fully executed
    
    if engine_task and not engine_task.done():
        try:
            await engine_task
        except asyncio.CancelledError:
            # Engine task can be cancelled before it could be awaited due to some reason
            # eg. ctrl+c
            pass
    
    await engine.quit()

asyncio.run(main())
