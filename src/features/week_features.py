# Fonction permettant d'ajouter des features "hebdomadaires" au niveau partie :

import pandas as pd


def add_week_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.sort_values(["player_id", "datetime_utc"]).copy()

    iso_calendar = df["datetime_utc"].dt.isocalendar()

    # Permet de gérer des parties jouées à cheval sur deux années (ex: 2023-12-31 et 2024-01-01 font partie de la même semaine)
    df["week_id"] = (
        iso_calendar["year"].astype(str)
        + "-W"
        + iso_calendar["week"].astype(str).str.zfill(2)
    )

    # Nombre de parties jouées par le joueur dans la semaine
    df["week_n_games"] = (
        df.groupby(["player_id", "week_id"])["game_id"]
        .transform("count")
    )

    # Score moyen de la semaine
    df["week_score"] = (
        df.groupby(["player_id", "week_id"])["result_player"]
        .transform("mean")
    )

    # Position de la partie dans la semaine
    df["week_position"] = (
        df.groupby(["player_id", "week_id"])
        .cumcount()
    )

    return df