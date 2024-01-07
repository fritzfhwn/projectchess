from chessdotcom import get_leaderboards, get_titled_players, get_country_players, Client, get_player_profile, \
    get_player_stats, get_player_games_by_month

class Request:
    Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. "
    )
    @staticmethod
    def gm_players():
        try:
            return get_titled_players("GM").json["players"]
        except Exception as e:
            print(f"Fehler beim Abrufen der GM-Spieler: {e}")
            return []

    @staticmethod
    def im_players():
        try:
            return get_titled_players("IM").json["players"]
        except Exception as e:
            print(f"Fehler beim Abrufen der IM-Spieler: {e}")
            return []

    @staticmethod
    def fm_players():
        try:
            return get_titled_players("FM").json["players"]
        except Exception as e:
            print(f"Fehler beim Abrufen der FM-Spieler: {e}")
            return []

    @staticmethod
    def blitz_leaderboard():
        try:
            return get_leaderboards().json["leaderboards"]["live_blitz"]
        except Exception as e:
            print(f"Fehler beim Abrufen des Blitz-Leaderboards: {e}")
            return []

    @staticmethod
    def bullet_leaderboard():
        try:
            return get_leaderboards().json["leaderboards"]["live_bullet"]
        except Exception as e:
            print(f"Fehler beim Abrufen des Bullet-Leaderboards: {e}")
            return []

    @staticmethod
    def get_user_games_by_month(username, year, month):
        try:
            return get_player_games_by_month(username, year, month).json["games"]
        except Exception as e:
            print(f"Fehler beim Abrufen von Spielen für {username} im Jahr {year}, Monat {month}: {e}")
            return []

    @staticmethod
    def get_user_profile(username):
        try:
            return get_player_profile(username).json["player"]
        except Exception as e:
            print(f"Fehler beim Abrufen des Profils von {username}: {e}")
            return {}

    @staticmethod
    def get_user_stats(username):
        try:
            return get_player_stats(username).json["stats"]
        except Exception as e:
            print(f"Fehler beim Abrufen der Statistiken von {username}: {e}")
            return {}
