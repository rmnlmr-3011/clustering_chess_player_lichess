from src.features.player_features import build_player_features
from src.labels.progression import build_progression_labels

import pandas as pd

def build_final_dataset(player_games: pd.DataFrame) -> pd.DataFrame:
    player_features = build_player_features(player_games)
    progression_labels = build_progression_labels(player_games)

    final_dataset = player_features.merge(
        progression_labels,
        on="player_id",
        how="inner"
    )

    return final_dataset