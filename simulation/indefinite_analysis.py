import asyncio
import chess
import chess.engine
import random

async def engine_analysis(engine: chess.engine.UciProtocol, board: chess.Board):
    with await engine.analysis(board) as analysis:
        async for info in analysis:
            score = info.get("score")
            seldepth = info.get("seldepth", 0)
            is_mate = score.is_mate() if score else None

            if score:
                print(score.white())

            if is_mate or seldepth > 60:
                break

async def main():
    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
    
    board = chess.Board()
    engine_task = None
    
    transport, engine = await chess.engine.popen_uci(r"C:\Users\2648a\dev\projects\cv\segmentation\stockfish\stockfish-windows-x86-64-avx2.exe")

    for i in range(len(moves)):
        # player thinking
        await asyncio.sleep(random.randint(1, 5))
        
        print(f"\nHalf move was made #{i + 1}: {moves[i]}")
        board.push_uci(moves[i])

        if engine_task and not engine_task.done():
            print("---ABORT ENGINE TASK ---")
            engine_task.cancel()
        
        engine_task = asyncio.create_task(engine_analysis(engine, board))
    
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
