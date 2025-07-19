import asyncio
import chess
import chess.engine
import random

async def engine_analysis(engine, board):
    with await engine.analysis(board) as analysis:
        async for info in analysis:
            score = info.get("score")
            seldepth = info.get("seldepth", 0)

            if score:
                print(score.white())

            if (score and score.is_mate()) or seldepth > 60:
                break

async def main():
    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
    
    board = chess.Board()
    engine_task = None
    
    transport, engine = await chess.engine.popen_uci(r"C:\Users\2648a\dev\projects\cv\segmentation\stockfish\stockfish-windows-x86-64-avx2.exe")

    for i in range(len(moves)):
        # player thinking
        await asyncio.sleep(random.randint(1, 5))
        
        print(f"\nPlayer made move #{i + 1}")
        board.push_uci(moves[i])

        if engine_task and not engine_task.done():
            print("---ABORT ENGINE TASK ---")
            engine_task.cancel()
        
        engine_task = asyncio.create_task(engine_analysis(engine, board))
    
    # for last exectution, when the main coroutine finished its stuff and only the engine_task is left to complete
    if engine_task and not engine_task.done():
        try:
            await engine_task
        except asyncio.CancelledError:
            # Engine task can be cancelled before it could be awaited due to some reason
            # eg. ctrl+c
            pass
    
    await engine.quit()

asyncio.run(main())
