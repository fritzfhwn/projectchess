from api import ChessAPIHandler
import utils
import re
import datetime as dt


class DataProcessor:

    @staticmethod
    def calculate_win_rate(df, result):
        """
        Calculates the win rate for each opening category based on a specified result.

        :param df: DataFrame containing player game data.
        :param result: The result to calculate win rate for (e.g., 'win', 'loss').
        :return: A DataFrame with opening categories and their corresponding win rate percentages.
        """
        def rate(group):
            wins = group[group['Reason'] == result].shape[0]
            total_games = group.shape[0]
            return wins / total_games * 100 if total_games > 0 else 0
        return df.groupby('Opening Category').apply(rate).reset_index(name=f'{result} %')

    @staticmethod
    def get_filtered_games(player, year, month):
        """
        Retrieves and processes a list of games for a specific player, year, and month.

        :param player: The username of the player.
        :param year: The year of the games to retrieve.
        :param month: The month of the games to retrieve.
        :return: A list of processed game data.
        """
        game_list = ChessAPIHandler.get_user_games_by_month(player, year, month)
        for game in game_list:
            for key in game.keys():
                if key == "end_time":
                    game[key] = (utils.date_conversion(game[key]))
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

    @staticmethod
    def filter_periods_from_start_and_end_date(start: utils.YearMonth, end: utils.YearMonth):
        """
        Generates a list of periods (year and month) between two given dates.

        :param start: The starting YearMonth object.
        :param end: The ending YearMonth object.
        :return: A list of dictionaries with 'year' and 'months' keys.
        """
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



    @staticmethod
    def get_result_reasons(player_list, mode, result, streamer):
        """
        Analyzes the reasons for game outcomes (loss or draw) for a specific player group.

        :param player_list: DataFrame containing player game data.
        :param mode: The game format to analyze (e.g., 'blitz', 'bullet', 'rapid').
        :param result: The game outcome to analyze (e.g., 'draw', 'loss').
        :param streamer: Boolean indicating whether to filter by streamers.
        :return: A Series with counts of each reason as a percentage.
        """
        df = player_list
        df = df[(df["Format"] == mode) & (df["Streamer"] == streamer)]

        result_types = {
            "loss": ["resigned", "timeout", "checkmated", "abandoned"],
            "draw": ["insufficient", "stalemate", "repetition", "timevsinsufficient", "50move", "agreed"]
        }
        df = df[df['Reason'].isin(result_types[result])]
        reasons_count = (df['Reason'].value_counts(normalize=True) * 100).round(2)

        return reasons_count
