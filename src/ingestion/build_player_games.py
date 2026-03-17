# Permet de construire la table player_games à partir d'une liste de parties brutes Berserk.

import pandas as pd

from src.ingestion.flatten_games import flatten_game
from src.ingestion.player_view import game_to_player_rows


def build_player_games(games: list[dict]) -> pd.DataFrame:

    player_rows = []

    for game in games:
        flat_game = flatten_game(game)
        rows = game_to_player_rows(flat_game)
        player_rows.extend(rows)

    df = pd.DataFrame(player_rows)
    return df