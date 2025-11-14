import os
from dotenv import load_dotenv
import requests as req
req.packages.urllib3.util.connection.HAS_IPV6 = False

load_dotenv(dotenv_path=".env", override=True)

LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

oauth_header = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
}

json_header = {
    "Accept": "application/json",
}

def set_username():
    url = "https://lichess.org/api/account"
    response = req.get(url=url, headers=oauth_header)
    os.environ["LICHESS_USERNAME"] = response.json().get("username")

def set_current_game_id():
    username = os.getenv("LICHESS_USERNAME")
    url = f"https://lichess.org/api/user/{username}/current-game"
    response = req.get(url=url, headers=json_header)
    os.environ["LICHESS_GAME_ID"] = response.json().get("id")

def make_move(uci):
    gameId = os.getenv("LICHESS_GAME_ID")
    url = f"https://lichess.org/api/board/game/{gameId}/move/{uci}"
    response = req.post(url=url, headers=oauth_header)
    print(response.json())

async def set_credentials():
    set_username()
    set_current_game_id()
