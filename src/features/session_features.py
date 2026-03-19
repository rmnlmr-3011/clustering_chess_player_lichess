# Fonctions permettant d'ajouter des features de session aux données de parties.
    # A préciser qu'on ne crée pas une table à part pour les sessions, mais plutôt qu'on ajoute des features de session à la table de parties.

import pandas as pd

SESSION_THRESHOLD = 60 * 60  # 1 heure


# Fonction permettant de créer les sessions et de les identifier par un session_id
def _add_sessions(df: pd.DataFrame) -> pd.DataFrame:

    df = df.sort_values(["player_id", "datetime_utc"]).copy()

    df["new_session"] = (
        df["delay_previous_game"].isna() |
        (df["delay_previous_game"] > SESSION_THRESHOLD)
    )

    df["session_id"] = df.groupby("player_id")["new_session"].cumsum()

    return df

# Fonction permettant de discrétiser le délai entre les sessions en catégories (A, B, C, D, E) (pour la feature discrete_delay_previous_session)
def _discretize_delay(seconds):
    if pd.isna(seconds):
        return None
    if seconds < 6 * 3600:
        return "A"
    elif seconds < 24 * 3600:
        return "B"
    elif seconds < 3 * 24 * 3600:
        return "C"
    elif seconds < 7 * 24 * 3600:
        return "D"
    else:
        return "E"

# Fonction permettant de créer les sessions et d'ajouter des features de session à la table de parties
def add_sessions(df: pd.DataFrame) -> pd.DataFrame:

    df = _add_sessions(df)

    # Index / position de la partie dans la session
    df["session_position"] = (
        df.groupby(["player_id", "session_id"])
        .cumcount()
    )

    # Nombre de parties dans la session
    df["session_size"] = (
        df.groupby(["player_id", "session_id"])["game_id"]
        .transform("count")
    )

    # Score moyen du joueur dans la session (moyenne de result_player)
    df["session_score"] = (
        df.groupby(["player_id", "session_id"])["result_player"]
        .transform("mean")
    )

    # Délai entre la session actuelle et la session précédente
    df["is_session_start"] = df["session_position"] == 0
    df["session_delay"] = df["delay_previous_game"].where(
        df["is_session_start"]
    )
    df["session_delay"] = (
        df.groupby(["player_id", "session_id"])["session_delay"]
        .transform("first")
    )

    # Discrétisation du délai entre les sessions
    df["session_discrete_delay"] = df["session_delay"].apply(_discretize_delay)

    return df