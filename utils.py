from dataclasses import dataclass
from datetime import datetime
from isocodes import countries
import api
import json
import re
import datetime as dt
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import dataframes

country_list = [{"name": country["name"], "code": country["alpha_2"]} for country in countries.items]

def opening_categories_and_results():
    return json.load(open("data/opening_and_result.json"))

opening_categories = opening_categories_and_results()

def assign_category(opening):
    for category, openings in opening_categories.items():
        if any(op in opening for op in openings):
            return category
    return 'None'


def calculate_win_rate(df, result):
    def rate(group):
        wins = group[group['Reason'] == result].shape[0]
        total_games = group.shape[0]
        return wins / total_games * 100 if total_games > 0 else 0
    return df.groupby('Opening Category').apply(rate).reset_index(name=f'{result} %')

def filter_openings(player_list, mode, result):
    df = player_list
    df = df[df["Format"] == mode]
    df = df.drop(
        ["Format", "Month", "Opponent Accuracy", "Country", "Opponent Elo", "Accuracy", "Streamer"],
        axis=1)

    df['Opening Category'] = df['Opening'].apply(assign_category)
    df['Reason'] = df['Reason'].apply(assign_category)
    df = df[df['Opening Category'] != 'None']

    win_rates = calculate_win_rate(df, result)
    win_rates = win_rates.set_index("Opening Category")

    return pickle.dump(win_rates, open(f"df_gm_{mode}_{result}.pkl", "wb"))


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
    json.dump(games_list, open("game_list_17_bis_21_im.json", "w"), indent=6)


def get_complete_profile(player_array):
    output = []
    modes = ["chess_rapid", "chess_blitz", "chess_bullet", "fide", "puzzle_rush"]
    categories = ["last", "best"]
    for player in player_array:
        print(player)
        stats_temp = filter_dictionary(api.Request.get_user_stats(player),
                                       modes)
        player_details = filter_dictionary(api.Request.get_user_profile(player),
                                           ["name", "username", "country", "is_streamer"])
        player_details["country"] = player_details["country"][34::]
        for item in country_list:
            if item["code"] == player_details["country"]:
                player_details["country"] = item["name"]
                break
        for mode in modes[0:3]:
            if mode in stats_temp:
                for category in categories:
                    if category in stats_temp[mode]:
                        stats_temp[mode][category]["date"] = date_conversion(stats_temp[mode][category]["date"])
        output.append({"details": player_details,
                       "stats": stats_temp})

    return json.dump(output, open("player_profile_list_gm.json", "w"), indent=6)


def prepare_individual_game_information(game_list, rating, year):
    data_object = {"player": [], "month": [], "format": [], "color": [], "opening": [], "elo": [], "opp elo": [], "reason": [],
                   "accuracy": [], "opp accuracy": []}

    for entry in game_list:
        for game in entry["games"]:
            if "time_class" in game.keys():
                if game["time_class"] in ["blitz", "bullet", "rapid"] and game["rules"] == "chess":
                    data_object["player"].append(entry["player"])
                    data_object["month"].append(entry["month"])
                    data_object["format"].append(game["time_class"])
                    if "pgn" in game.keys():
                        if "opening" in game["pgn"].keys():
                            data_object["opening"].append(game["pgn"]["opening"])
                        else:
                            data_object["opening"].append("None")
                    else:
                        data_object["opening"].append("None")
                    if game["white"]["username"].lower() == entry["player"]:
                        data_object["color"].append("White")
                        data_object["elo"].append(game["white"]["rating"])
                        data_object["opp elo"].append(game["black"]["rating"])
                        data_object["reason"].append(game["white"]["result"])
                        if "accuracies" in game.keys():
                            if "white" in game["accuracies"].keys():
                                data_object["accuracy"].append(game["accuracies"]["white"])
                            else:
                                data_object["accuracy"].append("undefined")
                            if "black" in game["accuracies"].keys():
                                data_object["opp accuracy"].append(game["accuracies"]["black"])
                            else:
                                data_object["opp accuracy"].append("undefined")
                        else:
                            data_object["accuracy"].append("undefined")
                            data_object["opp accuracy"].append("undefined")
                    else:
                        data_object["color"].append("Black")
                        data_object["elo"].append(game["black"]["rating"])
                        data_object["opp elo"].append(game["white"]["rating"])
                        data_object["reason"].append(game["black"]["result"])
                        if "accuracies" in game.keys():
                            if "black" in game["accuracies"].keys():
                                data_object["accuracy"].append(game["accuracies"]["black"])
                            else:
                                data_object["accuracy"].append("undefined")
                            if "white" in game["accuracies"].keys():
                                data_object["opp accuracy"].append(game["accuracies"]["white"])
                            else:
                                data_object["opp accuracy"].append("undefined")
                        else:
                            data_object["accuracy"].append("undefined")
                            data_object["opp accuracy"].append("undefined")

    df = pd.DataFrame(
        {
            "Player": data_object["player"],
            "Month": data_object["month"],
            "Format": data_object["format"],
            "Color": data_object["color"],
            "Opening": data_object["opening"],
            "Elo": data_object["elo"],
            "Opponent Elo": data_object["opp elo"],
            "Reason": data_object["reason"],
            "Accuracy": data_object["accuracy"],
            "Opponent Accuracy": data_object["opp accuracy"]
        }
    )

    gm = json.load(open("data/gm/player_profile_list_gm.json"))
    im = json.load(open("data/im/player_profile_list_im.json"))
    fm = json.load(open("data/fm/player_profile_list_fm.json"))
    player_details = gm + im + fm
    df["Country"] = "undefined"
    player_list = list(df['Player'].unique())
    df.set_index('Player', inplace=True)
    for entry in player_list:
        for player in player_details:
            if entry == player["details"]["username"]:
                df.loc[entry, "Country"] = player["details"]["country"]
                df.loc[entry, "Streamer"] = player["details"]["is_streamer"]
                break

    return pickle.dump(df, open(f"df_{rating}_individual_games_{year}.pkl", "wb"))


def get_result_reasons(player_list, mode, result, streamer):
    df = player_list
    df = df[(df["Format"] == mode) & (df["Streamer"] == streamer)]

    result_types = {
        "loss": ["resigned", "timeout", "checkmated", "abandoned"],
        "draw": ["insufficient", "stalemate", "repetition", "timevsinsufficient", "50move", "agreed"]
    }
    df = df[df['Reason'].isin(result_types[result])]
    reasons_count = (df['Reason'].value_counts(normalize=True) * 100).round(2)

    return reasons_count

def plot_result_reasons(player_list, mode, reason):

    streamer = get_result_reasons(player_list, mode, reason, True)
    non_streamer = get_result_reasons(player_list, mode, reason, False)

    streamer = streamer.reset_index()
    non_streamer = non_streamer.reset_index()

    categories = streamer['Reason']
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots()

    ax.bar(x - width/2, streamer['proportion'], width, label='Streamer')
    ax.bar(x + width/2, non_streamer['proportion'], width, label='Non Streamer')

    ax.set_ylabel('Percent')
    ax.set_title(f'{reason} reasons in {mode} for Streamer/Non Streamer')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def elo_progression(mode):
    dataframe = [dataframes.load_im_individual_2017(), dataframes.load_im_individual_2018(), dataframes.load_im_individual_2019(), dataframes.load_im_individual_2020(), dataframes.load_im_individual_2021(), dataframes.load_im_individual_2022(), dataframes.load_im_individual_2023()]

    year = 2017
    df = pd.DataFrame(columns=["Player", 2017, 2018, 2019, 2020, 2021, 2022, 2023])

    for entry in dataframe:
        entry = entry[entry["Format"] == mode]
        entry = entry.drop(["Format", "Month", "Opening", "Opponent Accuracy", "Country", "Color", "Opponent Elo", "Reason", "Accuracy", "Streamer"], axis=1)
        entry_grouped = entry.groupby(entry.index).mean().round()

        for player in entry_grouped.index:
            if player not in df['Player'].values:
                new_row = pd.DataFrame([[player] + [None]*(year - 2017) + [entry_grouped.at[player, 'Elo']] + [None]*(2023 - year)], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df.loc[df['Player'] == player, year] = entry_grouped.at[player, 'Elo']

        year += 1

    df = df.drop_duplicates(subset=["Player"]).reset_index(drop=True)
    df.sort_values(by="Player", ascending=True, inplace=True)

    return pickle.dump(df, open(f"elo_df_im_17_23-{mode}.pkl", "wb"))


def get_streamer_correlation(player_list, mode, size):
    df = player_list

    streamer_df = df[(df["Streamer"] == True) & (df["Format"] == mode)]
    non_streamer_df = df[(df["Streamer"] == False) & (df["Format"] == mode)]

    sample_size_streamer = min(len(streamer_df), size)
    sample_size_non_streamer = min(len(non_streamer_df), size)

    data_frame_streamer = streamer_df.sample(n=sample_size_streamer, replace=False)
    data_frame_non_streamer = non_streamer_df.sample(n=sample_size_non_streamer, replace=False)

    combined_df = pd.concat([data_frame_streamer, data_frame_non_streamer])

    combined_df = combined_df.drop(["Month", "Format", "Opening", "Opponent Accuracy", "Country", "Color"], axis=1)

    combined_df['Reason'] = np.where(combined_df['Reason'] == 'win', 1, 0)
    combined_df['Streamer'] = combined_df['Streamer'].astype(int)

    r, p_value = stats.pointbiserialr(combined_df['Streamer'], combined_df['Reason'])

    mean_win_percent_streamer = combined_df[combined_df['Streamer'] == 1]['Reason'].mean()
    mean_win_percent_non_streamer = combined_df[combined_df['Streamer'] == 0]['Reason'].mean()

    fig, ax = plt.subplots()
    positions = [0, 1]
    heights = [mean_win_percent_non_streamer, mean_win_percent_streamer]
    labels = ['Non-Streamer', 'Streamer']

    ax.bar(positions, heights, align='center', alpha=0.7, color=['blue', 'orange'])
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Win %')
    ax.set_title('Average Win Percentage by Streamer Status')
    return [fig, r, p_value]

def win_rate_accuracy_scatterplot(player_list):

    df = player_list
    df = df[df["Format"] == "blitz"]
    df = df[df["Accuracy"] != "undefined"]
    df = df.reset_index()

    player_counts = df['Player'].value_counts()
    players_to_keep = player_counts[player_counts >= 500].index.tolist()
    df = df[df['Player'].isin(players_to_keep)]

    df['Win %'] = df['Reason'].apply(lambda x: 1 if x == 'win' else 0)
    df = df.drop(
        ["Format", "Opening", "Month", "Opponent Accuracy", "Country", "Opponent Elo", "Streamer", "Color", "Elo"],
        axis=1)

    df = df.groupby('Player').agg({
        'Win %': lambda x: x.sum() / x.count() * 100,
        'Accuracy': 'mean'
    })
    df['Accuracy'] = pd.to_numeric(df['Accuracy'], errors='coerce')

    fig, ax = plt.subplots()
    sns.regplot(x='Win %', y='Accuracy', data=df, ax=ax)

    ax.set_xlim([10, 90])
    ax.set_ylim([75, 90])
    return fig
