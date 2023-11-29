import json

from chessdotcom import get_leaderboards, get_titled_players, get_country_players, Client, get_player_profile, \
    get_player_stats, get_player_games_by_month
from datetime import datetime
from isocodes import countries

Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
)
country_list = []

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
    for player in player_array:
        for entry in dates:
            for month in entry["months"]:
                games = get_player_games_by_month(player, entry["year"], month).json["games"]
                games_list.append({"player": player,
                                   "year": entry["year"],
                                   "month": month,
                                   "games": games})
        print(games_list)
    json.dump(games_list, open("game_list.json", "w"), indent=6)


def get_complete_profile(player_array):
    output = []
    for player in player_array:
        stats_temp = get_filtered_userstats(player)
        modes = ["chess_rapid", "chess_blitz", "chess_bullet"]
        categories = ["last", "best"]
        for mode in modes:
            if check_key(stats_temp, mode):
                for category in categories:
                    if check_key(stats_temp[mode], category):
                        stats_temp[mode][category]["date"] = date_conversion(stats_temp[mode][category]["date"])
                output.append({"details": get_filtered_userdetails(player),
                               "stats": stats_temp})
    return json.dump(output, open("complete_player_profile_list.json", "w"), indent=6)


