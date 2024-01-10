
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

Within the function, an api request is being made to extract a list of games of a given player for the respective year and month. The function then further checks if a string pattern exists (i.e. "ECOURL") and stores the information in a variable.
The game list has the following structure:

"games": [
    {
      "url": "https://www.chess.com/game/daily/576103712",
      "move_by": 0,
      "pgn": "[Event \"Let's Play!\"]\n[Site \"Chess.com\"]\n[Date \"2023.10.22\"]\n[Round \"2\"]\n[White \"erik\"]\n[Black \"Bombay_bullet1234\"]\n[Result \"*\"]\n[CurrentPosition \"r4r2/2nq1k1p/2p1b1pP/ppbpPpP1/3p1P2/3P4/PPPBN1BK/R3QR2 b - - 4 22\"]\n[Timezone \"UTC\"]\n[ECO \"C47\"]\n[ECOUrl \"https://www.chess.com/openings/Four-Knights-Game-4.g3-Bc5-5.Bg2-d6\"]\n[UTCDate \"2023.10.22\"]\n[UTCTime \"11:54:00\"]\n[WhiteElo \"1502\"]\n[BlackElo \"1418\"]\n[TimeControl \"1/604800\"]\n[StartTime \"11:54:00\"]\n[Link \"https://www.chess.com/game/daily/576103712\"]\n\n1. e4 {[%clk 165:09:02]} 1... e5 {[%clk 167:59:39]} 2. Nf3 {[%clk 167:50:39]} 2... Nc6 {[%clk 125:25:41]} 3. Nc3 {[%clk 165:31:34]} 3... Nf6 {[%clk 115:31:43]} 4. g3 {[%clk 167:59:53]} 4... Bc5 {[%clk 167:59:41]} 5. Bg2 {[%clk 167:59:18]} 5... d6 {[%clk 167:59:32]} 6. O-O {[%clk 166:54:54]} 6... O-O {[%clk 167:36:03]} 7. h3 {[%clk 167:58:08]} 7... Be6 {[%clk 167:59:05]} 8. d3 {[%clk 167:43:03]} 8... Qd7 {[%clk 101:26:19]} 9. Kh2 {[%clk 167:00:33]} 9... Nd4 {[%clk 67:37:11]} 10. Nxd4 {[%clk 167:24:42]} 10... exd4 {[%clk 0:01:32]} 11. Ne2 {[%clk 162:54:01]} 11... d5 {[%clk 167:57:34]} 12. e5 {[%clk 167:07:58]} 12... Ne8 {[%clk 167:46:07]} 13. f4 {[%clk 167:51:01]} 13... g6 {[%clk 23:25:30]} 14. g4 {[%clk 163:16:27]} 14... f5 {[%clk 149:27:17]} 15. g5 {[%clk 167:47:31]} 15... a5 {[%clk 118:28:01]} 16. Ng3 {[%clk 167:57:49]} 16... b5 {[%clk 167:58:50]} 17. h4 {[%clk 167:51:42]} 17... Kf7 {[%clk 167:59:01]} 18. h5 {[%clk 167:57:25]} 18... Ng7 {[%clk 167:40:59]} 19. Bd2 {[%clk 166:52:51]} 19... c6 {[%clk 126:54:52]} 20. h6 {[%clk 167:54:54]} 20... Ne8 {[%clk 98:03:54]} 21. Ne2 {[%clk 163:17:32]} 21... Nc7 {[%clk 93:09:57]} 22. Qe1 {[%clk 160:14:11]} *\n",
      "time_control": "1/604800",
      "last_activity": 1702784586,
      "rated": true,
      "turn": "black",
      "fen": "r4r2/2nq1k1p/2p1b1pP/ppbpPpP1/3p1P2/3P4/PPPBN1BK/R3QR2 b - - 4 22",
      "start_time": 1697975640,
      "time_class": "daily",
      "rules": "chess",
      "white": "https://api.chess.com/pub/player/erik",
      "black": "https://api.chess.com/pub/player/bombay_bullet1234"
    } ]

The data fetched often provides inconsistent or incomplete information. Sometimes keys will be missing in the dict, or in the pgn data can be missing due to abandoned games. Thus, the function implements some failsafes in order to process incomplete data. In the pgn, it has to be checked whether a playing pattern is present in order to cut unnecessary information (time-control is interesting but probably not viable to base an analysis on it for now, as it would also require the game position to be evaluated by an engine to gain information). 
The filtered game list will still provide all played moves in case it is needed for future analysys. 

---------------------

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
    json.dump(games_list, open("game_list_17_bis_21_im.json", "w"), indent=6)



Function will first extract a list of every year and its corresponding months, that fit in the range of the function args (start and enddate). The function then iterates over every player in the player array. It will then be iterated over the list of dates so that for every month a list of games will be created of the player that is currently being iterated over. The function returnes a list of every game of every player corresponding to the selected month and year within the given timespan.


------------------------------------------

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


Function returns the following list of jsons:

{
            "details": {
                  "name": "Tamas Banusz",
                  "username": "bancsoo",
                  "country": "Hungary",
                  "is_streamer": false
            },
            "stats": {
                  "chess_rapid": {
                        "last": {
                              "rating": 2602,
                              "date": "2023-02-02 18:27:44",
                              "rd": 95
                        },
                        "best": {
                              "rating": 2695,
                              "date": "2020-08-14 16:34:30",
                              "game": "https://www.chess.com/game/live/5333765576"
                        },
                        "record": {
                              "win": 13,
                              "loss": 7,
                              "draw": 12
                        }
                  },
                  "chess_blitz": {
                        "last": {
                              "rating": 2856,
                              "date": "2023-11-30 01:27:50",
                              "rd": 34
                        },
                        "best": {
                              "rating": 2941,
                              "date": "2022-06-17 16:41:08",
                              "game": "https://www.chess.com/game/live/14592492223"
                        },
                        "record": {
                              "win": 1480,
                              "loss": 1281,
                              "draw": 327
                        }
                  },
                  "chess_bullet": {
                        "last": {
                              "rating": 2714,
                              "date": "2020-12-02 11:13:57",
                              "rd": 70
                        },
                        "best": {
                              "rating": 2714,
                              "date": "2020-09-24 10:23:06",
                              "game": "https://www.chess.com/game/live/2870951587"
                        },
                        "record": {
                              "win": 38,
                              "loss": 26,
                              "draw": 9
                        }
                  },
                  "puzzle_rush": {
                        "best": {
                              "total_attempts": 50,
                              "score": 48
                        }
                  }
            }
      }

Especially country and streamer status is interesting but also other metrics can be used. For the analysys only streamer status was used. 

------------------------------------------

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

Loads the player profiles dumped from the previous function. Creates a dataframe with relevant data from individual games.
Appends streamer status and country from player profiles to the each game. Dumps the dataframe for faster usage.
Function arg "rating" is only used to create dynamic file names when returning thedataframe

------------------------------------------

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

    
    
This block of functions is used to filter every game in the dataframe by its opening, assign the game to an opening category (Flank Opening, Open, Semi-Open, Semi-Closed and Closed, Indian Defense) then calculates the average win/loss/draw rate of this
category depending on which argument is handed over to the function. args can be for instance: (gm_players, "blitz", "win")


------------------------------------------

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

By handing over streamer status (True/False) as arg the dataframe will be filtered by the respective list of streamers or non streamers. It will then calculate the percentage of reasons for draw or loss (depending on function arg) and returns the values.
The following function will use these values to build the bar plot:

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

------------------------------------------

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

Function calculates the average elo for every year from 2017 - 2023 for every IM. The performance of the function could vastly be enhanced by taking first and last game of every month, calculate the average and then calculate the yearly average for instance. Instead it takes every single game of the year and calculates the average elo. Because of this bad performance, a dataframe is being dumped and loaded to enhance loading times with streamlit. For future projects this will be handled more efficiently.

------------------------------------------

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


The function analyzes the relationship between being a streamer and the likelihood of winning in a specified game format. It starts by dividing the players into two groups based on their streamer status and the game format. Both groups are then sampled to ensure a balanced comparison, with the sample size limited by a function arg. The function processes the data by discarding irrelevant columns and converting the 'Reason' column to a binary format to represent wins and losses. It then calculates the point-biserial correlation coefficient and its p-value to assess the statistical significance of the relationship between being a streamer and winning. Additionally, the function computes and visualizes the average win percentages for both streamers and non-streamers, presenting these findings in a bar chart. The output includes the chart, the correlation coefficient, and the p-value, providing a comprehensive overview of the win rates in relation to the streamer status.

------------------------------------------


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

The function generates a scatter plot to explore the relationship between win rate and accuracy for players in the blitz format. It filters the provided player data to include only blitz format games and players with defined accuracy values. Further refinement is done by focusing on players with a minimum of 500 games. The function then calculates each player's win percentage and averages their accuracy. Irrelevant columns are dropped to streamline the data. The aggregated data is used to create a scatter plot using Seaborn's regplot, displaying each player's average accuracy against their win percentage.