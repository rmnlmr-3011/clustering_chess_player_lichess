# Code relatif à la sélection des joueurs retenus pour l'étude à partir du dataframe player_games brut.

from __future__ import annotations

from dataclasses import dataclass
from logging import config
from numpy.testing import verbose
import pandas as pd


@dataclass(frozen=True)
class PlayerSelectionConfig:
    min_games_in_window: int = 200
    max_games_in_window: int = 1000
    burnin_games: int = 20
    min_initial_elo: int = 1000
    max_initial_elo: int = 1400
    observation_window_days: int = 183

    require_rated: bool = True
    require_rapid: bool = True
    require_finished: bool = True

def select_player_games(
    df: pd.DataFrame,
    config: PlayerSelectionConfig | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Sélectionne les parties retenues pour l'étude à partir d'un dataframe
    player_games brut (1 ligne = 1 joueur dans 1 partie).

    Important :
    les `burnin_games` parties ignorées correspondent aux premières parties
    rapid, classées et terminées retenues après application des filtres bruts.

    Pipeline appliqué :
    1. validation des colonnes
    2. filtres bruts : rapid / rated / finished
    3. tri chronologique par joueur
    4. indexation des parties rapid/rated/finished
    5. suppression des `burnin_games` premières parties retenues
    6. filtre sur l'Elo initial après burn-in
    7. fenêtre d'observation fixe de `observation_window_days`
    8. filtre sur le nombre minimal de parties dans la fenêtre

    Retourne :
        player_games_selected
    """
    config = config or PlayerSelectionConfig()

    _validate_required_columns(df)

    work = df.copy()

    if verbose:
        _log_dataset_state("Initial", work)

    work = _apply_raw_game_filters(work, config)
    if verbose:
        _log_dataset_state("Après filtres bruts", work)

    work = _sort_games(work)
    work = _add_game_index(work)

    work = _drop_burnin_games(work, burnin_games=config.burnin_games)
    if verbose:
        _log_dataset_state(
            f"Après suppression des {config.burnin_games} premières parties rapid/rated/finished",
            work,
        )

    work = _filter_players_by_initial_elo(
        work,
        min_elo=config.min_initial_elo,
        max_elo=config.max_initial_elo,
    )
    if verbose:
        _log_dataset_state(
            f"Après filtre Elo initial [{config.min_initial_elo}, {config.max_initial_elo}]",
            work,
        )

    work = _filter_by_observation_window(
        work,
        window_days=config.observation_window_days,
    )
    if verbose:
        _log_dataset_state(
            f"Après fenêtre d'observation de {config.observation_window_days} jours",
            work,
        )

    work = _filter_players_by_game_count_in_window(
        work,
        min_games=config.min_games_in_window,
        max_games=config.max_games_in_window,
    )
    if verbose:
        _log_dataset_state(
            f"Après filtre nombre de parties [{config.min_games_in_window}, {config.max_games_in_window}]",
            work,
        )

    work = _finalize_output(work)

    _run_final_assertions(work, config)

    if verbose:
        _log_selected_summary(work)

    return work


# =====================================================================
# Validation
# =====================================================================

REQUIRED_COLUMNS = {
    "player_id",
    "game_id",
    "datetime_utc",
    "elo_player_before",
    "rated",
    "speed",
    "termination_type",
}


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Colonnes manquantes pour la sélection des joueurs : {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("Le dataframe fourni à select_player_games() est vide.")


# =====================================================================
# Filtres bruts au niveau partie
# =====================================================================

def _apply_raw_game_filters(
    df: pd.DataFrame,
    config: PlayerSelectionConfig,
) -> pd.DataFrame:
    work = df.copy()

    if config.require_rated:
        work = work[work["rated"] == True]

    if config.require_rapid:
        work = work[work["speed"].astype(str).str.lower() == "rapid"]

    if config.require_finished:
        work = work[work["termination_type"].notna()]
        work = work[
            ~work["termination_type"].astype(str).str.lower().isin({"created", "started"})
        ]

    return work


# =====================================================================
# Ordonnancement / indexation
# =====================================================================

def _sort_games(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(
        ["player_id", "datetime_utc", "game_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _add_game_index(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["rapid_game_index"] = work.groupby("player_id").cumcount()
    return work


# =====================================================================
# Burn-in
# =====================================================================

def _drop_burnin_games(df: pd.DataFrame, burnin_games: int) -> pd.DataFrame:
    return df[df["rapid_game_index"] >= burnin_games].copy()


# =====================================================================
# Filtre Elo initial
# =====================================================================

def _filter_players_by_initial_elo(
    df: pd.DataFrame,
    min_elo: int,
    max_elo: int,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    first_after_burnin = (
        df.sort_values(["player_id", "datetime_utc", "game_id"])
          .groupby("player_id", as_index=False)
          .first()
    )

    valid_players = first_after_burnin.loc[
        first_after_burnin["elo_player_before"].between(min_elo, max_elo, inclusive="both"),
        "player_id",
    ]

    return df[df["player_id"].isin(valid_players)].copy()


# =====================================================================
# Fenêtre d'observation
# =====================================================================

def _filter_by_observation_window(
    df: pd.DataFrame,
    window_days: int,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    work = df.copy()

    start_dt = work.groupby("player_id")["datetime_utc"].transform("min")
    elapsed_days = (work["datetime_utc"] - start_dt).dt.total_seconds() / 86400.0

    work["days_from_window_start"] = elapsed_days
    work = work[work["days_from_window_start"] <= window_days].copy()

    return work


# =====================================================================
# Filtre nombre minimal de parties
# =====================================================================

def _filter_players_by_game_count_in_window(
    df: pd.DataFrame,
    min_games: int,
    max_games: int,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    counts = df.groupby("player_id")["game_id"].count()

    valid_players = counts[
        (counts >= min_games) & (counts <= max_games)
    ].index

    return df[df["player_id"].isin(valid_players)].copy()

# =====================================================================
# Finalisation
# =====================================================================

def _finalize_output(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    work = (
        df.sort_values(["player_id", "datetime_utc", "game_id"], kind="mergesort")
          .reset_index(drop=True)
          .copy()
    )

    work["selected_game_index"] = work.groupby("player_id").cumcount()

    return work


# =====================================================================
# Assertions finales
# =====================================================================

def _run_final_assertions(
    df: pd.DataFrame,
    config: PlayerSelectionConfig,
) -> None:
    if df.empty:
        return

    if config.require_rated:
        assert (df["rated"] == True).all(), "Des parties non rated subsistent."

    if config.require_rapid:
        assert (df["speed"].astype(str).str.lower() == "rapid").all(), \
            "Des parties non rapid subsistent."

    counts = df.groupby("player_id")["game_id"].count()
    assert ((counts >= config.min_games_in_window) & (counts <= config.max_games_in_window)).all(), \
        "Des joueurs sont hors bornes sur le nombre de parties dans la fenêtre."

    first_games = (
        df.sort_values(["player_id", "datetime_utc", "game_id"])
          .groupby("player_id", as_index=False)
          .first()
    )
    assert first_games["elo_player_before"].between(
        config.min_initial_elo,
        config.max_initial_elo,
        inclusive="both",
    ).all(), "Des joueurs hors plage Elo subsistent."

    if "days_from_window_start" in df.columns:
        max_elapsed = df.groupby("player_id")["days_from_window_start"].max()
        assert (max_elapsed <= config.observation_window_days).all(), \
            "Fenêtre d'observation dépassée."

    assert df.duplicated(subset=["player_id", "game_id"]).sum() == 0, \
        "Doublons player_id/game_id détectés."


# =====================================================================
# Logging
# =====================================================================

def _log_dataset_state(label: str, df: pd.DataFrame) -> None:
    n_rows = len(df)
    n_players = df["player_id"].nunique() if "player_id" in df.columns else 0
    print(f"[{label}] rows={n_rows:,} | players={n_players:,}")


def _log_selected_summary(df: pd.DataFrame) -> None:
    counts = df.groupby("player_id")["game_id"].count()

    print("\n[Résumé final]")
    print(f"Joueurs retenus : {df['player_id'].nunique():,}")
    print(f"Lignes retenues  : {len(df):,}")
    print("Nb de parties par joueur :")
    print(counts.describe())

    first_games = (
        df.sort_values(["player_id", "datetime_utc", "game_id"])
          .groupby("player_id", as_index=False)
          .first()
    )

    print("\nElo initial dans la fenêtre :")
    print(first_games["elo_player_before"].describe())