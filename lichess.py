import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

gameId = os.getenv("LICHESS_GAME_ID")
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

headers = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
}

import httpx
import asyncio

async def api_call(uci):
    async with httpx.AsyncClient() as client:
        url = f"https://lichess.org/api/board/game/{gameId}/move/{uci}"
        response = await client.post(url=url, headers=headers)
        print(response.json())

def play_move(uci):
    asyncio.run(api_call(uci))
