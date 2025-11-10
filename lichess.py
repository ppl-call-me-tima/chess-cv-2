import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv(dotenv_path=".env", override=True)

LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

headers = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
}

async def make_move(uci):
    async with httpx.AsyncClient() as client:
        gameId = os.getenv("LICHESS_GAME_ID")
        url = f"https://lichess.org/api/board/game/{gameId}/move/{uci}"
        response = await client.post(url=url, headers=headers)
        print(response.json())
