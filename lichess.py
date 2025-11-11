import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv(dotenv_path=".env", override=True)

LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

post_headers = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
}

get_headers = {
    "Accept": "application/json",
}

params = {

}

async def set_username():
    async with httpx.AsyncClient() as client:
        url = "https://lichess.org/api/account"
        response = await client.get(url=url, headers=post_headers)
        os.environ["LICHESS_USERNAME"] = response.json().get("username")

async def set_current_game_id():
    async with httpx.AsyncClient() as client:
        username = os.getenv("LICHESS_USERNAME")
        url = f"https://lichess.org/api/user/{username}/current-game"
        response = await client.get(url=url, headers=get_headers)
        os.environ["LICHESS_GAME_ID"] = response.json().get("id")

async def make_move(uci):
    async with httpx.AsyncClient() as client:
        gameId = os.getenv("LICHESS_GAME_ID")
        url = f"https://lichess.org/api/board/game/{gameId}/move/{uci}"
        response = await client.post(url=url, headers=post_headers)
        print(response.json())

async def set_credentials():
    await set_username()
    await set_current_game_id()
