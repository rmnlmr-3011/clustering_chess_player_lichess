# Définition des features partie qui induisent une notion temporelle

import pandas as pd


# Fonction interne au module pour calculer le streak cumulatif après chaque partie
    # Une streak est une séquence de 2 victoires ou de 2 défaites consécutives
    # Valeur positive pour winstreak, négative pour losestreak
    # En cas de match nul, ou d'un résultat autre de la streak actuelle, la streak est réinitialisée à 0
def _compute_streak_after(df: pd.DataFrame) -> pd.Series:

    streaks = []

    for _, group in df.groupby("player_id"):
        current = 0
        player_streaks = []

        for r in group["result_player"]:
            if r == 1:
                current = current + 1 if current >= 0 else 1
            elif r == 0:
                current = current - 1 if current <= 0 else -1
            else:
                current = 0

            player_streaks.append(current)

        streaks.extend(player_streaks)

    return pd.Series(streaks, index=df.index)



# Fonction pour ajouter les features temporelles aux parties
def add_basic_temporal_features(df: pd.DataFrame) -> pd.DataFrame:

    # Tri des parties par joueur et par date
    df = df.sort_values(["player_id", "datetime_utc"]).copy()

    # Feature index : numéro de la partie par joueur selon son ordre chronologique
    df["index"] = df.groupby("player_id").cumcount()

    # Feature delay_previous_game : temps écoulé en secondes entre la partie courante et la partie précédente du même joueur
    df["delay_previous_game"] = (
        df.groupby("player_id")["datetime_utc"]
        .diff()
        .dt.total_seconds()
    )

    # Features décrivant la streak du joueur avant et après la partie courante
    df["streak_after"] = _compute_streak_after(df)
    df["streak_before"] = df.groupby("player_id")["streak_after"].shift(1)

    return df