import pickle
def load_pickle_file(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)

def load_im_elo_progression_blitz():
    return load_pickle_file('data/im/elo_df_im_17_23-blitz.pkl')

def load_im_elo_progression_bullet():
    return load_pickle_file('data/im/elo_df_im_17_23-bullet.pkl')

def load_im_elo_progression_rapid():
    return load_pickle_file('data/im/elo_df_im_17_23-rapid.pkl')

def load_gm_opening_results_2023_bullet():
    return [load_pickle_file('data/gm/df_gm_bullet_win.pkl'),
            load_pickle_file('data/gm/df_gm_bullet_loss.pkl'),
            load_pickle_file('data/gm/df_gm_bullet_draw.pkl')]

def load_fm_opening_results_2023_bullet():
    return [load_pickle_file('data/fm/df_fm_bullet_win.pkl'),
            load_pickle_file('data/fm/df_fm_bullet_loss.pkl'),
            load_pickle_file('data/fm/df_fm_bullet_draw.pkl')]

def load_im_individual_2023():
    return load_pickle_file('data/im/df_im_individual_games_2023.pkl')

def load_im_individual_2022():
    return load_pickle_file('data/im/df_im_individual_games_2022.pkl')

def load_im_individual_2021():
    return load_pickle_file('data/im/df_im_individual_games_2021.pkl')

def load_im_individual_2020():
    return load_pickle_file('data/im/df_im_individual_games_2020.pkl')

def load_im_individual_2019():
    return load_pickle_file('data/im/df_im_individual_games_2019.pkl')

def load_im_individual_2018():
    return load_pickle_file('data/im/df_im_individual_games_2018.pkl')

def load_im_individual_2017():
    return load_pickle_file('data/im/df_im_individual_games_2017.pkl')

def load_gm_individual_2023():
    return load_pickle_file('data/gm/df_gm_individual_games_2023.pkl')

def load_gm_individual_2022():
    return load_pickle_file('data/gm/df_gm_individual_games_2022.pkl')

def load_fm_individual_2023():
    return load_pickle_file('data/fm/df_fm_individual_games_2023.pkl')

def load_fm_individual_2022():
    return load_pickle_file('data/fm/df_fm_individual_games_2022.pkl')