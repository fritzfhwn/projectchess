import json
import re
from chessdotcom import get_leaderboards, get_titled_players, get_country_players, Client, get_player_profile, \
    get_player_stats, get_player_games_by_month
from datetime import datetime
from isocodes import countries

Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
)
country_list = [{"name": country["name"], "code": country["alpha_2"]} for country in countries.items]


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
    dataset = ["name", "username", "country", "is_streamer"]
    filtered_object = {}
    for data in dataset:
        if check_key(userdata, data):
            filtered_object[data] = userdata[data]
    return filtered_object


def get_filtered_userstats(user):
    userstats = get_player_stats(user).json["stats"]
    modes = ["chess_rapid", "chess_blitz", "chess_bullet", "fide", "puzzle_rush"]
    filtered_object = {}
    for mode in modes:
        if check_key(userstats, mode):
            filtered_object[mode] = userstats[mode]
    return filtered_object


def get_filtered_games(player, year, month):
    game_list = get_player_games_by_month(player, year, month).json["games"]
    for game in game_list:
        for key in game.keys():
            if key == "end_time":
                game[key] = date_conversion(game[key])
            if key == "pgn":
                date = ""
                opening = ""
                cleaned_moves = ""
                search_for_date = re.search(r'\[Date "(.*?)"', game[key])
                if search_for_date:
                    date = search_for_date.group(1)
                search_for_opening = re.search(r'\[ECOUrl "(.*?)"', game[key])
                if search_for_opening:
                    opening = search_for_opening.group(1)[31::]
                search_for_game_moves = re.search(r'\n\n(.*?)\n', game[key])
                if search_for_game_moves:
                    game_moves = search_for_game_moves.group(1)
                    cleaned_moves = re.sub(r"\{\[%clk [0-9:.]*\]\}", "", game_moves)
                    cleaned_moves = re.sub(r"\d+\.\.\. ?", "", cleaned_moves)
                game[key] = {
                    "date": date,
                    "opening": opening,
                    "moves": cleaned_moves}
    return game_list

def filter_periods_from_start_and_end_date(start, end):
    dates = []
    if start <= end <= datetime.now().strftime("%Y-%m"):
        counter_year = int(start[0:4:])
        counter_month = int(start[5:7:])
        while counter_year < int(end[0:4:]):
            months_list = []
            while counter_month <= 12:
                months_list.append(str(counter_month))
                counter_month += 1
            dates.append({"year": counter_year,
                          "months": months_list})
            counter_year += 1
            counter_month = 1
        if counter_year == int(end[0:4:]):
            months_list = []
            while counter_month <= int(end[5:7:]):
                months_list.append(str(counter_month))
                counter_month += 1
            dates.append({"year": counter_year,
                          "months": months_list})
    return dates


def get_games_from_player_by_period(startdate, enddate, player_array):
    dates = filter_periods_from_start_and_end_date(startdate, enddate)
    games_list = []
    player_counter = 1
    for player in player_array:
        for entry in dates:
            for month in entry["months"]:
                games = get_filtered_games(player, entry["year"], month)
                games_list.append({"player": player,
                                   "year": entry["year"],
                                   "month": month,
                                   "games": games})
        print(player, player_counter)
        player_counter += 1
    json.dump(games_list, open("game_list_2023_fm.json", "w"), indent=6)


def get_complete_profile(player_array):
    output = []
    for player in player_array:
        stats_temp = get_filtered_userstats(player)
        player_details = get_filtered_userdetails(player)
        player_details["country"] = player_details["country"][34::]
        for item in country_list:
            if item["code"] == player_details["country"]:
                player_details["country"] = item["name"]
                break
        modes = ["chess_rapid", "chess_blitz", "chess_bullet"]
        categories = ["last", "best"]
        for mode in modes:
            if check_key(stats_temp, mode):
                for category in categories:
                    if check_key(stats_temp[mode], category):
                        stats_temp[mode][category]["date"] = date_conversion(stats_temp[mode][category]["date"])
        output.append({"details": player_details,
                       "stats": stats_temp})

    return json.dump(output, open("complete_player_profile_list.json", "w"), indent=6)

get_games_from_player_by_period("2023-01", "2023-11", fm_players())