import json
import pickle
import pandas as pd
import utils
from pickle_loaders import DataImporter
from data_processor import DataProcessor
from api import ChessAPIHandler
from isocodes import countries

class DataHandler:

    @staticmethod
    def load_data(file_path, format):
        """
        Load data from a file in either JSON or pickle format.

        :param file_path: Path to the file to be loaded.
        :param format: The format of the file ('json' or 'pickle').
        :return: The data loaded from the file.
        """
        if format == 'json':
            with open(file_path, 'r') as file:
                return json.load(file)
        elif format == 'pickle':
            with open(file_path, 'rb') as file:
                return pickle.load(file)

    @staticmethod
    def save_data(data, file_path, format):
        """
        Save data to a file in either JSON or pickle format.

        :param data: Data to be saved.
        :param file_path: Path to the file where data will be saved.
        :param format: The format for saving the data ('json' or 'pickle').
        """
        if format == 'json':
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=6)
        elif format == 'pickle':
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)

    country_list = [{"name": country["name"], "code": country["alpha_2"]} for country in countries.items]
    opening_categories = load_data("data/opening_and_result.json", "json")

    @staticmethod
    def assign_category(opening):
        """
        Assign a chess opening to its respective category.

        :param opening: The chess opening to categorize.
        :return: The category of the opening, or 'None' if not categorized.
        """
        for category, openings in DataHandler.opening_categories.items():
            if any(op in opening for op in openings):
                return category
        return 'None'

    @staticmethod
    def filter_openings(player_list, mode, result):
        """
        Filter openings from a list of players based on game format and result.

        :param player_list: List of player data.
        :param mode: Game format (e.g., 'blitz', 'bullet', 'rapid').
        :param result: The result to filter by (e.g., 'win', 'loss', 'draw').
        :return: A DataFrame with filtered opening categories and win rates.
        """
        df = player_list
        df = df[df["Format"] == mode]
        df = df.drop(
            ["Format", "Month", "Opponent Accuracy", "Country", "Opponent Elo", "Accuracy", "Streamer"],
            axis=1)

        df['Opening Category'] = df['Opening'].apply(DataHandler.assign_category)
        df['Reason'] = df['Reason'].apply(DataHandler.assign_category)
        df = df[df['Opening Category'] != 'None']

        win_rates = DataProcessor.calculate_win_rate(df, result)
        win_rates = win_rates.set_index("Opening Category")

        DataHandler.save_data(win_rates, f"df_gm_{mode}_{result}.pkl", "pickle")



    @staticmethod
    def save_individual_game_information(game_list, rating, year):
        """
        Process and save individual game information for players as well as player information like
        country or streamer status.

        :param game_list: List of games to process.
        :param rating: The rating category (e.g., 'gm', 'im', 'fm').
        :param year: The year of the games.
        """
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

        gm = DataHandler.load_data("data/gm/player_profile_list_gm.json", "json")
        im = DataHandler.load_data("data/gm/player_profile_list_im.json", "json")
        fm = DataHandler.load_data("data/gm/player_profile_list_fm.json", "json")
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

        DataHandler.save_data(df, f"df_{rating}_individual_games_{year}.pkl", "pickle")


    @staticmethod
    def save_elo_progression(mode):
        """
        Calculate and save the Elo progression of IM-players from 2017 to 2023 in a specific mode.

        :param mode: The game mode to calculate Elo progression for (e.g., 'blitz', 'bullet', 'rapid').
        """
        dataframe = [DataImporter.load_data("im", year, "individual") for year in range(2017, 2024)]
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

        file_path = f"df_im_elo_{mode}.pkl"
        DataHandler.save_data(df, file_path, 'pickle')

    @staticmethod
    def get_games_from_player_by_period(startdate, enddate, player_array):
        """
        Get games played by a list of players within a specified period.

        :param startdate: The start date of the period.
        :param enddate: The end date of the period.
        :param player_array: Array of player usernames.
        :return: A list of games played by the players in the specified period.
        """
        dates = DataProcessor.filter_periods_from_start_and_end_date(startdate, enddate)
        games_list = []

        for player in player_array:
            for entry in dates:
                for month in entry["months"]:
                    games = DataProcessor.get_filtered_games(player, entry["year"], month)
                    games_list.append({"player": player,
                                       "year": entry["year"],
                                       "month": month,
                                       "games": games})

        DataHandler.save_data(games_list, "game_list_17_bis_21_im.json", "json")

    @staticmethod
    def get_complete_profile(player_array):
        """
        Get complete profiles for a list of players, including stats and details.

        :param player_array: Array of player usernames.
        :return: Player profiles with details and stats.
        """
        output = []
        modes = ["chess_rapid", "chess_blitz", "chess_bullet", "fide", "puzzle_rush"]
        categories = ["last", "best"]
        for player in player_array:
            stats_temp = utils.filter_dictionary(ChessAPIHandler.get_user_stats(player),
                                           modes)
            player_details = utils.filter_dictionary(ChessAPIHandler.get_user_details(player),
                                               ["name", "username", "country", "is_streamer"])
            player_details["country"] = player_details["country"][34::]
            for item in DataHandler.country_list:
                if item["code"] == player_details["country"]:
                    player_details["country"] = item["name"]
                    break
            for mode in modes[0:3]:
                if mode in stats_temp:
                    for category in categories:
                        if category in stats_temp[mode]:
                            stats_temp[mode][category]["date"] = utils.date_conversion(stats_temp[mode][category]["date"])
            output.append({"details": player_details,
                           "stats": stats_temp})

        return DataHandler.save_data(output, "player_profile_list_gm.json", "json")
