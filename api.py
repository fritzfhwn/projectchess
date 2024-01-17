import logging
import requests
from chessdotcom import get_leaderboards, get_titled_players, get_player_profile, get_player_stats, get_player_games_by_month, Client

class ChessAPIHandler:
    """
    A handler class for interacting with a Chess API.

    This class provides methods to make various API requests related to chess data,
    including player information, game statistics, and leaderboard data.
    """
    def __init__(self):
        """
        Initializes the ChessAPIHandler instance and configures the API client.
        """
        self.client_config()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def client_config():
        """
        Configures the client for making API requests, specifically setting the User-Agent.
        """
        Client.request_config["headers"]["User-Agent"] = "My Python Application"

    @staticmethod
    def make_api_request(func, *args, **kwargs):
        """
        Makes an API request using a specified function and arguments.

        :param func: The API function to be called.
        :param args: Positional arguments for the API function.
        :param kwargs: Keyword arguments for the API function.
        :return: The JSON response from the API if the request is successful; otherwise, None.
        """
        try:
            response = func(*args, **kwargs)
            return response.json
        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler bei der API-Anfrage: {e}")
            return None

    def get_players(self, title):
        """
        Retrieves a list of players with a specific title.

        :param title: The title of the players to retrieve (e.g., 'GM', 'IM').
        :return: A list of players with the specified title.
        """
        return self.make_api_request(get_titled_players, title).get("players", [])

    def get_leaderboard(self, leaderboard_type):
        """
        Retrieves the leaderboard for a specific type.

        :param leaderboard_type: The type of leaderboard to retrieve (e.g., 'blitz', 'bullet').
        :return: A list of players in the specified leaderboard.
        """
        return self.make_api_request(get_leaderboards).get("leaderboards", {}).get(leaderboard_type, [])

    def get_user_games_by_month(self, username, year, month):
        """
        Retrieves games played by a user in a specific month and year.

        :param username: The username of the player.
        :param year: The year of the games.
        :param month: The month of the games.
        :return: A list of games played by the user in the specified time period.
        """
        return self.make_api_request(get_player_games_by_month, username, year, month).get("games", [])

    def get_user_profile(self, username):
        """
        Retrieves the profile information of a user.

        :param username: The username of the player.
        :return: A dictionary containing the player's profile information.
        """
        return self.make_api_request(get_player_profile, username).get("player", {})

    def get_user_stats(self, username):
        """
        Retrieves the statistical information of a user.

        :param username: The username of the player.
        :return: A dictionary containing the player's statistical information.
        """
        return self.make_api_request(get_player_stats, username).get("stats", {})

