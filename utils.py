from dataclasses import dataclass
from datetime import datetime

@dataclass
class YearMonth():
    year: int
    month: int

def date_conversion(timestamp):
    """
    Converts a Unix timestamp to a human-readable date string.

    :param timestamp: Unix timestamp to be converted.
    :return: A string representing the date in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def filter_dictionary(data_dict: dict, key_list: list) -> dict:
    """
    Filters a dictionary, retaining only the keys specified in the key list.

    :param data_dict: The dictionary to be filtered.
    :param key_list: A list of keys to retain in the dictionary.
    :return: A new dictionary containing only the keys specified in key_list.
    """
    return {
        key: value
        for key, value in data_dict.items()
        if key in key_list
    }
