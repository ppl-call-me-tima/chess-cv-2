import chess
from logger import log

from helpers.engine_analysis.shared_resource import shared_resource

async def engine_analysis(engine: chess.engine.UciProtocol, board: chess.Board):
    with await engine.analysis(board) as analysis:
        async for info in analysis:
            score = info.get("score")
            seldepth = info.get("seldepth", 0)
            is_mate = score.is_mate() if score else None

            if score:
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
