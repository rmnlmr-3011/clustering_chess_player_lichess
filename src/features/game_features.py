# Fonction qui regroupe toutes les fonctions pour les features temporelles des parties

import numpy as np
import pandas as pd

from .temporal_features import add_basic_temporal_features
from .session_features import add_sessions
from .day_features import add_day_features
from .week_features import add_week_features



def build_game_features(df: pd.DataFrame) -> pd.DataFrame:

    features = _init_game_features(df)

    features = add_basic_temporal_features(features)
    features = add_sessions(features)
    features = add_day_features(features)
    features = add_week_features(features)

    return features



def _init_game_features(df: pd.DataFrame) -> pd.DataFrame:

    features = df.copy()
    features["datetime_utc"] = pd.to_datetime(features["datetime_utc"], utc=True, errors="coerce")

    features = features.dropna(subset=["player_id"])

    features = features.sort_values(["player_id", "datetime_utc", "game_id"]).reset_index(drop=True)

    return features
