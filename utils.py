from dataclasses import dataclass
from datetime import datetime
from isocodes import countries
import api
import json
import re
import datetime as dt
import pandas as pd
import numpy as np

country_list = [{"name": country["name"], "code": country["alpha_2"]} for country in countries.items]


@dataclass
class YearMonth():
    year: int
    month: int


def date_conversion(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def filter_dictionary(data_dict: dict, key_list: list) -> dict:
    return {
        key: value
        for key, value in data_dict.items()
        if key in key_list
    }


def get_filtered_games(player, year, month):
    game_list = api.Request.get_user_games_by_month(player, year, month)
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


def filter_periods_from_start_and_end_date(start: YearMonth, end: YearMonth):
    dates = []
    start = dt.datetime(start.year, start.month, 1)
    end = dt.datetime(end.year, end.month, 1)
    if start <= end <= dt.datetime.now():
        counter_year = start.year
        counter_month = start.month
        while counter_year < end.year:
            months_list = []
            while counter_month <= 12:
                months_list.append(str(counter_month))
                counter_month += 1
            dates.append({"year": counter_year,
                          "months": months_list})
            counter_year += 1
            counter_month = 1
        if counter_year == end.year:
            months_list = []
            while counter_month <= end.month:
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
    json.dump(games_list, open("game_list_2023_im.json", "w"), indent=6)


def get_complete_profile(player_array):
    output = []
    modes = ["chess_rapid", "chess_blitz", "chess_bullet", "fide", "puzzle_rush"]
    categories = ["last", "best"]
    for player in player_array:
        stats_temp = filter_dictionary(api.Request.get_user_stats(player),
                                       modes)
        player_details = filter_dictionary(api.Request.get_user_profile(player),
                                           ["name", "username", "country", "is_streamer"])
        player_details["country"] = player_details["country"][34::]
        for item in country_list:
            if item["code"] == player_details["country"]:
                player_details["country"] = item["name"]
                break
        for mode in modes[0:2]:
            if mode in stats_temp:
                for category in categories:
                    if category in stats_temp[mode]:
                        stats_temp[mode][category]["date"] = date_conversion(stats_temp[mode][category]["date"])
        output.append({"details": player_details,
                       "stats": stats_temp})

    return json.dump(output, open("complete_player_profile_list_test.json", "w"), indent=6)


def create_dataframe_from_games_list(game_list, mode):
    g_acc_array = []
    g_ab_array = []
    g_win_array = []
    g_ww_array = []
    g_wb_array = []
    g_draw_array = []
    g_dw_array = []
    g_db_array = []
    g_loss_array = []
    g_lw_array = []
    g_lb_array = []

    result = {"l": ["resigned", "timeout", "checkmated", "abandoned"],
              "d": ["insufficient", "stalemate", "repetition", "timevsinsufficient", "50move", "agreed"]
              }

    player_array = [game_list.loc[i]['player'] for i in game_list.index]
    month_array = [game_list.loc[i]['month'] for i in game_list.index]
    game_count_array = [
        sum(1 for entry in game_list.loc[i]['games'] if entry["time_class"] == mode and entry["rules"] == "chess") for i
        in game_list.index]

    for i in game_list.index:
        accuracy_array = []
        ab_array = []
        win_array = []
        ww_array = []
        wb_array = []
        draw_array = []
        dw_array = []
        db_array = []
        loss_array = []
        lw_array = []
        lb_array = []
        avg_acc = 0
        avg_ab = 0
        for entry in game_list.loc[i]['games']:
            if entry["time_class"] == mode and entry["rules"] == "chess":
                white = True
                if entry["black"]["username"].lower() == game_list.loc[i]['player']:
                    white = False
                    for key in result.keys():
                        for value in result[key]:
                            if key == "l" and value == entry["black"]["result"]:
                                loss_array.append(1)
                                lb_array.append(1)
                            if key == "d" and value == entry["black"]["result"]:
                                draw_array.append(1)
                                db_array.append(1)
                    if entry["black"]["result"] == "win":
                        win_array.append(1)
                        wb_array.append(1)
                else:
                    for key in result.keys():
                        for value in result[key]:
                            if key == "l" and value == entry["white"]["result"]:
                                loss_array.append(1)
                                lw_array.append(1)
                            if key == "d" and value == entry["white"]["result"]:
                                draw_array.append(1)
                                dw_array.append(1)
                    if entry["white"]["result"] == "win":
                        win_array.append(1)
                        ww_array.append(1)
                if "accuracies" in entry.keys():
                    if white:
                        accuracy_array.append(entry["accuracies"]["white"])
                    else:
                        ab_array.append(entry["accuracies"]["black"])
                if len(accuracy_array) > 0:
                    avg_acc = sum(accuracy_array) / len(accuracy_array)
                if len(ab_array) > 0:
                    avg_ab = sum(ab_array) / len(ab_array)

        g_acc_array.append(avg_acc)
        g_ab_array.append(avg_ab)
        g_win_array.append(len(win_array))
        g_ww_array.append(len(ww_array))
        g_wb_array.append(len(wb_array))
        g_draw_array.append(len(draw_array))
        g_dw_array.append(len(dw_array))
        g_db_array.append(len(db_array))
        g_loss_array.append(len(loss_array))
        g_lw_array.append(len(lw_array))
        g_lb_array.append(len(lb_array))

    g_acc_array = np.array(g_acc_array)
    g_win_array = np.array(g_win_array)
    g_ww_array = np.array(g_ww_array)
    g_wb_array = np.array(g_wb_array)
    g_draw_array = np.array(g_draw_array)
    g_dw_array = np.array(g_dw_array)
    g_db_array = np.array(g_db_array)
    g_loss_array = np.array(g_loss_array)
    g_lb_array = np.array(g_lb_array)
    g_lw_array = np.array(g_lw_array)
    game_count_array = np.array(game_count_array)

    with np.errstate(divide='ignore', invalid='ignore'):
        g_win_percent = np.where(game_count_array != 0, 100 * g_win_array / game_count_array, 0)
        g_draw_percent = np.where(game_count_array != 0, 100 * g_draw_array / game_count_array, 0)
        g_loss_percent = np.where(game_count_array != 0, 100 * g_loss_array / game_count_array, 0)

        total_games_white = g_ww_array + g_dw_array + g_lw_array
        g_ww_percent = np.where(total_games_white != 0, 100 * g_ww_array / total_games_white, 0)
        g_dw_percent = np.where(total_games_white != 0, 100 * g_dw_array / total_games_white, 0)
        g_lw_percent = np.where(total_games_white != 0, 100 * g_lw_array / total_games_white, 0)

        total_games_black = g_lb_array + g_db_array + g_wb_array
        g_wb_percent = np.where(total_games_black != 0, 100 * g_wb_array / total_games_black, 0)
        g_db_percent = np.where(total_games_black != 0, 100 * g_db_array / total_games_black, 0)
        g_lb_percent = np.where(total_games_black != 0, 100 * g_lb_array / total_games_black, 0)

    return pd.DataFrame(
        {"Player": player_array,
         "Month": month_array,
         "Games": game_count_array,
         "Wins": g_win_array,
         "Draws": g_draw_array,
         "Losses": g_loss_array,
         "Win %": np.round(g_win_percent, 2),
         "Draw %": np.round(g_draw_percent, 2),
         "Loss %": np.round(g_loss_percent, 2),
         "W% White": np.round(g_ww_percent, 2),
         "D% White": np.round(g_dw_percent, 2),
         "L% White": np.round(g_lw_percent, 2),
         "W% Black": np.round(g_wb_percent, 2),
         "D% Black": np.round(g_db_percent, 2),
         "L% Black": np.round(g_lb_percent, 2),
         "Acc w white": np.round(g_acc_array, 2),
         "Acc w black": np.round(g_ab_array, 2)
         })
