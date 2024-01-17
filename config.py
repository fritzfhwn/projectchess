from pathlib import Path

class Config:
    DATA_DIR = Path(__file__).resolve().parent.joinpath("data")

