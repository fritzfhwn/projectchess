from chessdotcom import get_leaderboards, get_titled_players, get_country_players, Client, get_player_profile, \
    get_player_stats
from datetime import datetime
from isocodes import countries
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
)
# response = requests.get(url, headers=headers)
username = ""
year = ""
month = ""
country_list = []
game_details = f"https://api.chess.com/pub/player/{username}/games/{year}/{month}"

for country in countries.items:
    country_list.append({"name": country["name"], "code": country["alpha_2"]})

def check_key(object, key):
    if key in object.keys():
        return True
    else:
        return False

def date_conversion(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def gm_players():
    return get_titled_players("GM").json["players"]


def im_players():
    return get_titled_players("IM").json["players"]


def fm_players():
    return get_titled_players("FM").json["players"]


def blitz_leaderboard():
    return get_leaderboards().json["leaderboards"]["live_blitz"]


def bullet_leaderboard():
    return get_leaderboards().json["leaderboards"]["live_bullet"]


def get_filtered_userdetails(user):
    userdata = get_player_profile(user).json["player"]
    if check_key(userdata, "name"):
        return {
            "name": userdata["name"],
            "username": user,
            "country": userdata["country"][34::],
            "is_streamer": userdata["is_streamer"]
        }


def get_filtered_userstats(user):
    userstats = get_player_stats(user).json["stats"]
    return {
        "rapid": userstats["chess_rapid"],
        "blitz": userstats["chess_blitz"],
        "bullet": userstats["chess_bullet"],
        "fide": userstats["fide"],
        "puzzle_rush": userstats["puzzle_rush"]
    }
