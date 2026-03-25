# Définition de plusieurs métriques de progression. 

# La métrique principale est elo_slope_per_game

import numpy as np
import pandas as pd


def _safe_slope(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]

    if len(x) < 2:
        return np.nan
    if np.std(x) == 0:
        return np.nan

    return np.polyfit(x, y, 1)[0]


def _elo_slope_per_game(df: pd.DataFrame) -> pd.Series:

    df = df.sort_values(["player_id", "datetime_utc", "game_id"]).copy()

    # index de partie dans la fenêtre d'observation
    df["game_index"] = df.groupby("player_id").cumcount()

    def compute(x):
        return _safe_slope(x["game_index"], x["elo_player_after"])

    return df.groupby("player_id").apply(compute)


def _elo_slope_per_day(df: pd.DataFrame) -> pd.Series:

    df = df.sort_values(["player_id", "datetime_utc", "game_id"]).copy()

    first_dt = df.groupby("player_id")["datetime_utc"].transform("min")
    df["days_from_start"] = (
        (df["datetime_utc"] - first_dt).dt.total_seconds() / 86400.0
    )

    def compute(x):
        return _safe_slope(x["days_from_start"], x["elo_player_after"])

    return df.groupby("player_id").apply(compute)


def _elo_gain(df: pd.DataFrame) -> pd.Series:

    ordered = df.sort_values(["player_id", "datetime_utc", "game_id"])

    first_elo = ordered.groupby("player_id")["elo_player_before"].first()
    last_elo = ordered.groupby("player_id")["elo_player_after"].last()

    return last_elo - first_elo


def _elo_gain_per_game(df: pd.DataFrame) -> pd.Series:

    gain = _elo_gain(df)
    n_games = df.groupby("player_id")["game_id"].count()

    out = gain / (n_games - 1)
    out[n_games < 2] = np.nan
    return out


def build_progression_labels(df: pd.DataFrame) -> pd.DataFrame:

    labels = _init_progression_labels(df)

    labels["elo_gain"] = _elo_gain(df)
    labels["elo_gain_per_game"] = _elo_gain_per_game(df)
    labels["elo_slope_per_game"] = _elo_slope_per_game(df)
    labels["elo_slope_per_day"] = _elo_slope_per_day(df)

    return labels.reset_index()


def _init_progression_labels(df: pd.DataFrame) -> pd.DataFrame:

    player_ids = df["player_id"].dropna().unique()
    labels = pd.DataFrame(index=sorted(player_ids))
    labels.index.name = "player_id"
    return labels

