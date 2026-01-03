import requests as req
req.packages.urllib3.util.connection.HAS_IPV6 = False
from chess import Color, WHITE, BLACK

class LichessManager:
    def __init__(self):
        # TODO: maybe impleent a file-handling system where you check for previous used username to auto-use default values
        self.username = None
        self.current_game_id = None
        self.colour: Color | None = None

        self.oauth_header = {}
        self.json_header = {
            "Accept": "application/json",
        }
    
    def set_token(self, token):
        if not token.startswith("lip_"):
            return None
        
        self.oauth_header = {
            "Authorization": f"Bearer {token}"
        }

        self.set_username()
        return self.username

    def set_username(self):
        url = "https://lichess.org/api/account"
        response = req.get(url=url, headers=self.oauth_header)
        self.username = response.json().get("username")

    def set_current_game_id_and_colour(self):
        username = self.username if self.username else ""
        url = f"https://lichess.org/api/user/{username}/current-game"
        response = req.get(url=url, headers=self.json_header)
        self.current_game_id = response.json().get("id")
        
        white_player = response.json().get("players", {}).get("white", {}).get("user", {}).get("name")
        black_player = response.json().get("players", {}).get("black", {}).get("user", {}).get("name")

        if white_player == self.username:
            self.colour = WHITE
        elif black_player == self.username:
            self.colour = BLACK

    def make_move(self, uci):
        game_id = self.current_game_id if self.current_game_id else ""
        url = f"https://lichess.org/api/board/game/{game_id}/move/{uci}"
        response = req.post(url=url, headers=self.oauth_header)
        print(response.json())

    def set_credentials(self):
        self.set_username()
        self.set_current_game_id_and_colour()

    def reset_current_game_id(self):
        self.current_game_id = None

    def is_lichess_connected(self):
        return bool(self.username and self.current_game_id)
