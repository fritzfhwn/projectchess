import pickle
from config import Config

class DataImporter:
    @staticmethod
    def load_pickle_file(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)

    @classmethod
    def load_data(cls, category, year, game_type):
        file_path = Config.DATA_DIR.joinpath(f"{category}/df_{category}_{game_type}_{year}.pkl")
        return cls.load_pickle_file(file_path)

    @classmethod
    def load_elo_progression(cls, category, game_type):
        file_path = Config.DATA_DIR.joinpath(f"{category}/df_{category}_elo_{game_type}.pkl")
        return cls.load_pickle_file(file_path)

    @classmethod
    def load_opening_results(cls, category, game_type, year):
        file_paths = [Config.DATA_DIR.joinpath(f"{category}/df_{category}_{game_type}_win_{year}.pkl"),
                      Config.DATA_DIR.joinpath(f"{category}/df_{category}_{game_type}_loss_{year}.pkl"),
                      Config.DATA_DIR.joinpath(f"{category}/df_{category}_{game_type}_draw_{year}.pkl")]

        return [cls.load_pickle_file(path) for path in file_paths]



