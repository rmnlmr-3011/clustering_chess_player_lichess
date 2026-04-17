# Code pour regrouper les features par thème,
# lister celles retenues pour le clustering,
# celles écartées du clustering,
# et celles gardées pour l'analyse.

# === Features retenues pour le clustering ===

STYLE_FEATURES = [
    "mean_ply_count",
    "opening_diversity",
    "opening_concentration",
]

ENDGAME_FEATURES = [
    "draw_ratio",
]

STREAK_FEATURES = [
    "score_when_winstreak",
    "score_when_losestreak",
    "delay_ratio_when_winstreak",
    "delay_ratio_when_losestreak",
]

GLOBAL_RHYTHM_FEATURES = [
    "cv_games_per_day",
    "cv_games_per_week",
    "cv_games_interval",
]

SESSION_FEATURES = [
    "cv_sessions_interval",
    "entropy_sessions_interval",
    "mean_games_per_session",
    "cv_games_per_session",
]

CONTEXT_FEATURES = [
    "weekday_bias",
    "color_bias",
]

# === Features gardées pour analyse uniquement ===

PERFORMANCE_FEATURES = [
    "session_length_performance_slope",
    "within_session_performance_slope",
    "games_per_day_performance_slope",
    "games_per_week_performance_slope",
]

PROGRESSION_LABELS = [
    "elo_gain",
    "elo_gain_per_game",
    "elo_slope_per_game",
    "elo_slope_per_day",
]

# === Features explicitement exclues du clustering ===

DROPPED_CLUSTERING_FEATURES = [
    "player_id",
    "main_opening_white",
    "main_opening_black",
    "abandon_rate",
    "time_loss_rate",
    "streak_resilience_bias",
    "abandon_rate_when_losestreak",
    "time_loss_rate_when_losestreak",
    "increment_game_ratio",
]

# === Groupement thématique des features de clustering ===

FEATURE_GROUPS = {
    "style": STYLE_FEATURES,
    "endgame": ENDGAME_FEATURES,
    "streaks": STREAK_FEATURES,
    "global_rhythm": GLOBAL_RHYTHM_FEATURES,
    "sessions": SESSION_FEATURES,
    "context": CONTEXT_FEATURES,
}

# === Listes utiles ===

SELECTED_CLUSTERING_FEATURES = (
    STYLE_FEATURES
    + ENDGAME_FEATURES
    + STREAK_FEATURES
    + GLOBAL_RHYTHM_FEATURES
    + SESSION_FEATURES
    + CONTEXT_FEATURES
)

ANALYSIS_ONLY_FEATURES = PERFORMANCE_FEATURES + PROGRESSION_LABELS

EXCLUDED_FROM_CLUSTERING = DROPPED_CLUSTERING_FEATURES + ANALYSIS_ONLY_FEATURES

ALL_DEFINED_FEATURES = (
    SELECTED_CLUSTERING_FEATURES
    + ANALYSIS_ONLY_FEATURES
    + DROPPED_CLUSTERING_FEATURES
)

FEATURE_GROUP_SIZES = {
    group_name: len(group_features)
    for group_name, group_features in FEATURE_GROUPS.items()
}

# === Sorties finales étape 5 ===

FEATURES_TO_DROP_UNIVARIATE = []

FEATURES_TO_DROP_CORR = [
    "opening_concentration",
    "cv_sessions_interval",
]

FEATURES_TO_TRANSFORM = [
    "cv_games_interval",
    "cv_games_per_week",
    "mean_games_per_session",
]

SELECTED_FEATURE_COLS_FINAL = [
    "mean_ply_count",
    "opening_diversity",
    "draw_ratio",
    "score_when_winstreak",
    "score_when_losestreak",
    "delay_ratio_when_winstreak",
    "delay_ratio_when_losestreak",
    "cv_games_interval",
    "cv_games_per_day",
    "cv_games_per_week",
    "entropy_sessions_interval",
    "mean_games_per_session",
    "cv_games_per_session",
    "weekday_bias",
    "color_bias",
]

FEATURE_GROUPS_UPDATED = {
    "style": [
        "mean_ply_count",
        "opening_diversity",
    ],
    "endgame": [
        "draw_ratio",
    ],
    "streaks": [
        "score_when_winstreak",
        "score_when_losestreak",
        "delay_ratio_when_winstreak",
        "delay_ratio_when_losestreak",
    ],
    "global_rhythm": [
        "cv_games_per_day",
        "cv_games_per_week",
        "cv_games_interval",
    ],
    "sessions": [
        "entropy_sessions_interval",
        "mean_games_per_session",
        "cv_games_per_session",
    ],
    "context": [
        "weekday_bias",
        "color_bias",
    ],
}