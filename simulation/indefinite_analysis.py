import asyncio
import random

async def engine_analysis(fen):
    print(f"-initiate engine task {fen}")
    for i in range(1, 10):
        # engine speed slowing down
        await asyncio.sleep(1)
        
        print(f"Engine streaming data at depth: {i}")
    print(f"analysis complete {fen}")

async def main():
    positions = ["fen1", "fen2", "fen3", "fen4", "fen5", "fen6", "fen7", "fen8", "fen9", "fen10"]
    
    engine_task = None
    
    for i in range(len(positions)):
        # player thinking
        await asyncio.sleep(random.randint(1, 10))
        
        print(f"\nPlayer made move #{i + 1}")

        if engine_task and not engine_task.done():
            print("---ABORT ENGINE TASK ---")
            engine_task.cancel()
        
        engine_task = asyncio.create_task(engine_analysis(positions[i]))
    
    # for last exectution, when the main coroutine finished its stuff and only the engine_task is left to complete
    if engine_task:
        try:
            await engine_task
        except asyncio.CancelledError:
            # Engine task can be cancelled before it could be awaited due to some reason
            # eg. ctrl+c
            pass

asyncio.run(main())
