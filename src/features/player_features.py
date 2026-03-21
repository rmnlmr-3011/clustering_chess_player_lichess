# Fonction pour calculer les features du joueur. La structure du code décompose ces features en 8 catégories :

    # Style de jeu
        # - mean_ply_count
        # - main_opening_white
        # - main_opening_black
        # - opening_diversity
        # - opening_concentration

    # Comportement en fin de partie
        # - abandon_rate
        # - time_loss_rate
        # - draw_ratio

    # Rapport aux streaks
        # - score_when_winstreak
        # - score_when_losestreak
        # - streak_resilience_bias
        # - abandon_rate_when_losestreak
        # - time_loss_rate_when_losestreak
        # - delay_ratio_when_winstreak
        # - delay_ratio_when_losestreak

    # Rythme de jeu global
        # - cv_games_per_day
        # - cv_games_per_week
        # - cv_games_interval

    # Structure des sessions
        # - cv_sessions_interval
        # - entropy_sessions_interval
        # - mean_games_per_session
        # - cv_games_per_session

    # Contexte de jeu
        # - increment_game_ratio
        # - weekday_bias
        # - color_bias

    # Dynamique de performance
        # - session_length_performance_slope
        # - within_session_performance_slope
        # - games_per_day_performance_slope
        # - games_per_week_performance_slope

    # Progression générale
        # - progression_volatility
        # - plateau_ratio
        # - mean_plateau_length


import numpy as np
import pandas as pd

def build_player_features(df: pd.DataFrame) -> pd.DataFrame:

    features = _init_player_features(df)

    features = _add_style_features(df, features)
    features = _add_endgame_behavior_features(df, features)
    features = _add_streak_features(df, features)
    features = _add_global_rhythm_features(df, features)
    features = _add_session_structure_features(df, features)
    features = _add_context_features(df, features)
    features = _add_performance_dynamics_features(df, features)
    features = _add_general_progression_features(df, features)

    return features.reset_index()

####################################################################################################

def _init_player_features(df: pd.DataFrame) -> pd.DataFrame:

    player_ids = df["player_id"].dropna().unique()
    features = pd.DataFrame(index=sorted(player_ids))
    features.index.name = "player_id"
    return features

####################################################################################################

def _add_style_features(df, features):

    features["mean_ply_count"] = _mean_ply_count(df)
    features["main_opening_white"] = _main_opening_by_color(df, color="white")
    features["main_opening_black"] = _main_opening_by_color(df, color="black")
    features["opening_diversity"] = _opening_diversity(df)
    features["opening_concentration"] = _opening_concentration(df)
    return features


OPENING_COL = "opening_family"   # variable temporaire


def _mean_ply_count(df: pd.DataFrame) -> pd.Series:

    return df.groupby("player_id")["ply_count"].mean()


def _main_opening_by_color(df: pd.DataFrame, color: str) -> pd.Series:

    sub = df[df["color_player"] == color].copy()

    if sub.empty:
        return pd.Series(dtype="object")

    sub = sub.dropna(subset=[OPENING_COL])

    if sub.empty:
        return pd.Series(dtype="object")

    def mode_opening(x: pd.Series):
        counts = x.value_counts()
        if counts.empty:
            return np.nan

        max_count = counts.max()
        candidates = sorted(counts[counts == max_count].index.tolist())
        return candidates[0]

    return sub.groupby("player_id")[OPENING_COL].apply(mode_opening)


# Fonction pour calculer l'entropie de Shannon d'une distribution discrète. Utile pour mesurer la diversité des ouvertures, par exemple.
def _entropy_from_series(x: pd.Series) -> float:

    x = x.dropna()
    if x.empty:
        return np.nan

    p = x.value_counts(normalize=True)
    return float(-(p * np.log(p)).sum())


def _opening_diversity_by_color(df: pd.DataFrame, color: str) -> pd.Series:

    sub = df[df["color_player"] == color].copy()
    if sub.empty:
        return pd.Series(dtype="float64")

    return sub.groupby("player_id")[OPENING_COL].apply(_entropy_from_series)


def _opening_diversity(df: pd.DataFrame) -> pd.Series:

    white = _opening_diversity_by_color(df, color="white").rename("white")
    black = _opening_diversity_by_color(df, color="black").rename("black")

    tmp = pd.concat([white, black], axis=1)
    return tmp.mean(axis=1, skipna=True)


def _opening_concentration_by_color(df: pd.DataFrame, color: str) -> pd.Series:

    sub = df[df["color_player"] == color].copy()

    if sub.empty:
        return pd.Series(dtype="float64")

    sub = sub.dropna(subset=[OPENING_COL])

    if sub.empty:
        return pd.Series(dtype="float64")

    def concentration(x: pd.Series) -> float:
        counts = x.value_counts()
        if counts.empty:
            return np.nan
        return float(counts.max() / counts.sum())

    return sub.groupby("player_id")[OPENING_COL].apply(concentration)


def _opening_concentration(df: pd.DataFrame) -> pd.Series:

    white = _opening_concentration_by_color(df, color="white").rename("white")
    black = _opening_concentration_by_color(df, color="black").rename("black")

    tmp = pd.concat([white, black], axis=1)
    return tmp.mean(axis=1, skipna=True)

####################################################################################################

def _add_endgame_behavior_features(df, features):
    features["abandon_rate"] = _abandon_rate(df)
    features["time_loss_rate"] = _time_loss_rate(df)
    features["draw_ratio"] = _draw_ratio(df)
    return features

def _draw_ratio(df: pd.DataFrame) -> pd.Series:
    return df.groupby("player_id").apply(
        lambda x: (
            (x["termination_type"] == "draw")
        ).mean()
    )

def _abandon_rate(df: pd.DataFrame) -> pd.Series:
    return df.groupby("player_id").apply(
        lambda x: (
            (x["termination_type"] == "resign") &
            (x["result_player"] == 0)
        ).mean()
    )

def _time_loss_rate(df: pd.DataFrame) -> pd.Series:
    return df.groupby("player_id").apply(
        lambda x: (
            (x["termination_type"] == "timeout") &
            (x["result_player"] == 0)
        ).mean()
    )


####################################################################################################


# Seuils permettant de considérer une streak comme winstreak ou losestreak
WINSTREAK_THRESHOLD = 2
LOSESTREAK_THRESHOLD = -2


def _add_streak_features(df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    features["score_when_winstreak"] = _score_when_winstreak(df)
    features["score_when_losestreak"] = _score_when_losestreak(df)
    features["streak_resilience_bias"] = (
        features["score_when_winstreak"] - features["score_when_losestreak"]
    )
    features["abandon_rate_when_losestreak"] = _abandon_rate_when_losestreak(df)
    features["time_loss_rate_when_losestreak"] = _time_loss_rate_when_losestreak(df)
    features["delay_ratio_when_winstreak"] = _delay_ratio_when_winstreak(df)
    features["delay_ratio_when_losestreak"] = _delay_ratio_when_losestreak(df)
    return features


def _score_when_winstreak(df: pd.DataFrame) -> pd.Series:
    sub = df[df["streak_before"] >= WINSTREAK_THRESHOLD]
    return sub.groupby("player_id")["result_player"].mean()


def _score_when_losestreak(df: pd.DataFrame) -> pd.Series:
    sub = df[df["streak_before"] <= LOSESTREAK_THRESHOLD]
    return sub.groupby("player_id")["result_player"].mean()


def _abandon_rate_when_losestreak(df: pd.DataFrame) -> pd.Series:
    def compute(group: pd.DataFrame) -> float:
        mask_ls = group["streak_before"] <= LOSESTREAK_THRESHOLD
        denom = mask_ls.sum()
        if denom == 0:
            return np.nan
        num = (
            (group["termination_type"] == "resign")
            & (group["result_player"] == 0)
            & mask_ls
        ).sum()
        return num / denom

    return df.groupby("player_id").apply(compute)


def _time_loss_rate_when_losestreak(df: pd.DataFrame) -> pd.Series:
    def compute(group: pd.DataFrame) -> float:
        mask_ls = group["streak_before"] <= LOSESTREAK_THRESHOLD
        denom = mask_ls.sum()
        if denom == 0:
            return np.nan
        num = (
            (group["termination_type"] == "timeout")
            & (group["result_player"] == 0)
            & mask_ls
        ).sum()
        return num / denom

    return df.groupby("player_id").apply(compute)


def _delay_ratio_when_winstreak(df: pd.DataFrame) -> pd.Series:
    def compute(group: pd.DataFrame) -> float:
        overall = group["delay_previous_game"].mean()
        if pd.isna(overall) or overall == 0:
            return np.nan

        delay_ws = group.loc[
            group["streak_before"] >= WINSTREAK_THRESHOLD,
            "delay_previous_game"
        ].mean()

        if pd.isna(delay_ws):
            return np.nan

        return delay_ws / overall

    return df.groupby("player_id").apply(compute)


def _delay_ratio_when_losestreak(df: pd.DataFrame) -> pd.Series:
    def compute(group: pd.DataFrame) -> float:
        overall = group["delay_previous_game"].mean()
        if pd.isna(overall) or overall == 0:
            return np.nan

        delay_ls = group.loc[
            group["streak_before"] <= LOSESTREAK_THRESHOLD,
            "delay_previous_game"
        ].mean()

        if pd.isna(delay_ls):
            return np.nan

        return delay_ls / overall

    return df.groupby("player_id").apply(compute)

####################################################################################################

def _add_global_rhythm_features(df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    features["cv_games_interval"] = _cv_games_interval(df)
    features["cv_games_per_day"] = _cv_games_per_day(df)
    features["cv_games_per_week"] = _cv_games_per_week(df)
    return features

def _cv_games_interval(df: pd.DataFrame) -> pd.Series:
    def compute(x):
        delays = x["delay_previous_game"].dropna()
        if len(delays) == 0:
            return np.nan

        mean = delays.mean()
        std = delays.std()

        if mean == 0 or pd.isna(mean):
            return np.nan

        return std / mean

    return df.groupby("player_id").apply(compute)

def _cv_games_per_day(df: pd.DataFrame) -> pd.Series:

    daily = (
        df[["player_id", "day_date_utc", "day_n_games"]]
        .drop_duplicates()
    )

    def compute(x):
        values = x["day_n_games"]

        mean = values.mean()
        std = values.std()

        if mean == 0 or pd.isna(mean):
            return np.nan

        return std / mean

    return daily.groupby("player_id").apply(compute)

def _cv_games_per_week(df: pd.DataFrame) -> pd.Series:

    weekly = (
        df[["player_id", "week_id", "week_n_games"]]
        .drop_duplicates()
    )

    def compute(x):
        values = x["week_n_games"]

        mean = values.mean()
        std = values.std()

        if mean == 0 or pd.isna(mean):
            return np.nan

        return std / mean

    return weekly.groupby("player_id").apply(compute)

####################################################################################################

def _add_session_structure_features(df, features):
    features["cv_sessions_interval"] = _cv_sessions_interval(df)
    features["entropy_sessions_interval"] = _entropy_sessions_interval(df)
    features["mean_games_per_session"] = _mean_games_per_session(df)
    features["cv_games_per_session"] = _cv_games_per_session(df)
    return features


def _mean_games_per_session(df: pd.DataFrame) -> pd.Series:

    sessions = (
        df.groupby(["player_id", "session_id"])
        .agg(n_games=("game_id", "count"))
        .reset_index()
    )

    return sessions.groupby("player_id")["n_games"].mean()


def _cv_games_per_session(df: pd.DataFrame) -> pd.Series:

    sessions = (
        df.groupby(["player_id", "session_id"])
        .agg(n_games=("game_id", "count"))
        .reset_index()
    )

    def compute(x):
        mean = x.mean()
        std = x.std()

        if mean == 0 or pd.isna(mean):
            return np.nan

        return std / mean

    return sessions.groupby("player_id")["n_games"].apply(compute)


def _cv_sessions_interval(df: pd.DataFrame) -> pd.Series:

    sessions = (
        df.groupby(["player_id", "session_id"])
        .agg(session_delay=("session_delay", "first"))
        .reset_index()
    )

    def compute(x):
        delays = x["session_delay"].dropna()

        if len(delays) == 0:
            return np.nan

        mean = delays.mean()
        std = delays.std()

        if mean == 0 or pd.isna(mean):
            return np.nan

        return std / mean

    return sessions.groupby("player_id").apply(compute)


def _entropy_sessions_interval(df: pd.DataFrame) -> pd.Series:

    sessions = (
        df.groupby(["player_id", "session_id"])
        .agg(delay=("session_discrete_delay", "first"))
        .reset_index()
    )

    def compute(x):
        values = x["delay"].dropna()

        if len(values) == 0:
            return np.nan

        probs = values.value_counts(normalize=True)

        return -np.sum(probs * np.log(probs))

    return sessions.groupby("player_id").apply(compute)



####################################################################################################

def _add_context_features(df, features):
    features["increment_game_ratio"] = _increment_game_ratio(df)
    features["weekday_bias"] = _weekday_bias(df)
    features["color_bias"] = _color_bias(df)
    return features


def _color_bias(df: pd.DataFrame) -> pd.Series:

    def compute(x):
        white = x[x["color_player"] == "white"]["result_player"]
        black = x[x["color_player"] == "black"]["result_player"]

        if len(white) == 0 or len(black) == 0:
            return np.nan

        return white.mean() - black.mean()

    return df.groupby("player_id").apply(compute)


def _increment_game_ratio(df: pd.DataFrame) -> pd.Series:

    return df.groupby("player_id")["has_increment"].mean()


def _weekday_bias(df: pd.DataFrame) -> pd.Series:

    def compute(x):
        weekday = x[x["weekday"] <= 4]["result_player"]
        weekend = x[x["weekday"] >= 5]["result_player"]

        if len(weekday) == 0 or len(weekend) == 0:
            return np.nan

        return weekday.mean() - weekend.mean()

    return df.groupby("player_id").apply(compute)


####################################################################################################

def _add_performance_dynamics_features(df, features):
    features["session_length_performance_slope"] = _session_length_performance_slope(df)
    features["within_session_performance_slope"] = _within_session_performance_slope(df)
    features["games_per_day_performance_slope"] = _games_per_day_performance_slope(df)
    features["games_per_week_performance_slope"] = _games_per_week_performance_slope(df)
    return features

####################################################################################################

def _add_general_progression_features(df, features):
    features["progression_volatility"] = _progression_volatility(df)
    features["plateau_ratio"] = _plateau_ratio(df)
    features["mean_plateau_length"] = _mean_plateau_length(df)
    return features


