# Fonction permettant d'ajouter des features "quotidiennes" au niveau partie :

import pandas as pd


def add_day_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.sort_values(["player_id", "datetime_utc"]).copy()

    # Date sans l'heure
    df["day_date_utc"] = df["datetime_utc"].dt.date

    # Nombre de parties jouées par le joueur dans la journée
    df["day_n_games"] = (
        df.groupby(["player_id", "day_date_utc"])["game_id"]
        .transform("count")
    )

    # Score moyen de la journée
    df["day_score"] = (
        df.groupby(["player_id", "day_date_utc"])["result_player"]
        .transform("mean")
    )

    # Position de la partie dans la journée
    df["day_position"] = (
        df.groupby(["player_id", "day_date_utc"])
        .cumcount()
    )

    return df