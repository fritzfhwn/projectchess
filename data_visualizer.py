import matplotlib.pyplot as plt
from scipy import stats
from data_processor import DataProcessor
import seaborn as sns
import pandas as pd
import numpy as np

class Visualizer:
    @staticmethod
    def win_rate_accuracy_scatterplot(player_list):
        """
        Creates a scatter plot showing the correlation between win rate and accuracy for players.

        :param player_list: A DataFrame containing player data.
        :return: A list containing the matplotlib figure, win rate standard deviation, win rate mean,
                 accuracy standard deviation, and accuracy mean.
        """

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

        win_mean = df['Win %'].mean()
        accuracy_mean = df['Accuracy'].mean()
        win_std = df['Win %'].std()
        accuracy_std = df['Accuracy'].std()

        fig, ax = plt.subplots()
        sns.regplot(x='Win %', y='Accuracy', data=df, ax=ax)

        ax.set_xlim([10, 90])
        ax.set_ylim([75, 90])
        return [fig, win_std, win_mean, accuracy_std, accuracy_mean]

    @staticmethod
    def get_streamer_correlation(player_list, mode, size):
        """
        Analyzes the correlation between being a streamer and winning in a specific game format.

        :param player_list: A DataFrame containing player data.
        :param mode: The game format to analyze (e.g., 'blitz', 'bullet', 'rapid').
        :param size: The number of samples to take from each group (streamer and non-streamer).
        :return: A list containing the matplotlib figure, correlation coefficient, and p-value.
        """

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

    @staticmethod
    def plot_result_reasons(player_list, mode, reason):
        """
        Plots the distribution of reasons for game results (win/loss/draw) for streamers and non-streamers.

        :param player_list: A DataFrame containing player data.
        :param mode: The game format to analyze (e.g., 'blitz', 'bullet', 'rapid').
        :param reason: The game outcome reason to analyze (e.g., 'win', 'loss', 'draw').
        :return: A matplotlib figure showing the distribution of reasons.
        """

        streamer = DataProcessor.get_result_reasons(player_list, mode, reason, True)
        non_streamer = DataProcessor.get_result_reasons(player_list, mode, reason, False)

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
