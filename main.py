import api
import utils
import pandas as pd


def main():
    # utils.get_games_from_player_by_period(utils.YearMonth(2023, 1), utils.YearMonth(2023, 11), api.Request.im_players())

    im_2023 = pd.read_json('data/im/game_list_2023_im.json')
    print(utils.create_dataframe_from_games_list(im_2023, "bullet"))


if __name__ == '__main__':
    main()
