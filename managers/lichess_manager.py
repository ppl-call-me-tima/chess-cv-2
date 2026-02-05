import requests as req
req.packages.urllib3.util.connection.HAS_IPV6 = False
from chess import Color, WHITE, BLACK
from helpers.logger import log

class LichessManager:
    def __init__(self):
        self.username = None
        self.current_game_id = None
        self.colour: Color | None = None

        self.oauth_header = {}
        self.json_header = {
            "Accept": "application/json",
        }
    
    def set_oauth_header(self, token):
        if not token.startswith("lip_"):
            return

        self.oauth_header = {
            "Authorization": f"Bearer {token}"
        }

    def fetch_username(self, token):
        self.set_oauth_header(token)
        try:
            if self.oauth_header:
                url = "https://lichess.org/api/account"
                response = req.get(url=url, headers=self.oauth_header)
                self.username = response.json().get("username")
                return self.username
        except Exception as e:
            print(f"Error while trying to fetch username: {e}")
            return None

    def set_current_game_id_and_colour(self):
        if self.username:
            url = f"https://lichess.org/api/user/{self.username}/current-game"
            response = req.get(url=url, headers=self.json_header)
            self.current_game_id = response.json().get("id")
            
            white_player = response.json().get("players", {}).get("white", {}).get("user", {}).get("name")
            black_player = response.json().get("players", {}).get("black", {}).get("user", {}).get("name")

            if white_player == self.username:
                self.colour = WHITE
            elif black_player == self.username:
                self.colour = BLACK

    def make_move(self, uci):
        """
        Returns False if error occurs while sending move using Lichess Board API, else True.
        
        :param uci: The move in `UCI` notation.
        """
        try:
            game_id = self.current_game_id if self.current_game_id else ""
            url = f"https://lichess.org/api/board/game/{game_id}/move/{uci}"
            response = req.post(url=url, headers=self.oauth_header)
            print(response.json())
            return True
        except Exception as e:
            log(f"Error in sending move to Lichess: {e.__str__()}")
            return False

    def reset_current_game_id(self):
        self.current_game_id = None

    def is_lichess_connected(self):
        return bool(self.username and self.current_game_id)
