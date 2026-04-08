# Code relatif à la construction du pool de joueurs candidats via une expansion à partir de seeds, et un préfiltrage léger.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time


@dataclass(frozen=True)
class CandidateSamplingConfig:
    # Expansion
    #max_games_per_seed: int = 50
    max_games_per_candidate: int = 30
    expansion_rounds: int = 1

    # Préfiltrage léger
    min_current_rapid_rating: int = 900
    max_current_rapid_rating: int = 1600
    require_rapid_perf: bool = True

    # Robustesse / débit
    sleep_seconds: float = 0.2
    verbose: bool = True


def build_candidate_player_pool(
    client: Any,
    seed_player_ids: list[str],
    config: CandidateSamplingConfig | None = None,
) -> list[str]:
    """
    Construit un pool de joueurs candidats à partir :
    1. d'une liste initiale de seeds
    2. d'une expansion via les adversaires rencontrés en rapid
    3. d'un préfiltrage léger via l'API users

    Hypothèse :
    - `client` est un client berserk ou un wrapper exposant des méthodes compatibles.
    """

    config = config or CandidateSamplingConfig()

    seeds = _normalize_player_ids(seed_player_ids)
    if not seeds:
        raise ValueError("seed_player_ids est vide après normalisation.")

    if config.verbose:
        print(f"[Sampling] Seeds initiaux : {len(seeds)}")

    all_candidates: set[str] = set(seeds)
    frontier: set[str] = set(seeds)

    for round_idx in range(config.expansion_rounds):
        if config.verbose:
            print(f"[Sampling] Round d'expansion {round_idx + 1}/{config.expansion_rounds}")

        new_opponents = _expand_once_via_opponents(
            client=client,
            player_ids=sorted(frontier),
            max_games_per_player=config.max_games_per_seed,
            sleep_seconds=config.sleep_seconds,
            verbose=config.verbose,
        )

        new_opponents -= all_candidates
        all_candidates |= new_opponents
        frontier = new_opponents

        if config.verbose:
            print(
                f"[Sampling] Nouveaux adversaires ajoutés : {len(new_opponents)} | "
                f"Pool total : {len(all_candidates)}"
            )

        if not frontier:
            break

    filtered_candidates = prefilter_candidate_players(
        client=client,
        player_ids=sorted(all_candidates),
        config=config,
    )

    if config.verbose:
        print(
            f"[Sampling] Pool final après préfiltrage : {len(filtered_candidates)} "
            f"joueurs"
        )

    return filtered_candidates


def prefilter_candidate_players(
    client: Any,
    player_ids: list[str],
    config: CandidateSamplingConfig | None = None,
) -> list[str]:
    """
    Préfiltre les joueurs candidats avec des critères légers :
    - existence d'une perf rapid
    - rapid rating courant dans une plage large [900, 1600] par défaut

    Remarque :
    ce filtre n'est volontairement PAS le filtre scientifique final.
    """
    config = config or CandidateSamplingConfig()

    kept: list[str] = []

    for idx, player_id in enumerate(_normalize_player_ids(player_ids), start=1):
        public_data = _safe_get_public_data(client, player_id)
        rapid_perf = _safe_get_rapid_performance(client, player_id)

        keep = _passes_light_prefilter(
            public_data=public_data,
            rapid_perf=rapid_perf,
            config=config,
        )

        if keep:
            kept.append(player_id)

        if config.verbose and idx % 25 == 0:
            print(
                f"[Prefilter] Joueurs traités : {idx}/{len(player_ids)} | "
                f"retenus : {len(kept)}"
            )

        time.sleep(config.sleep_seconds)

    return kept


def collect_raw_games_for_players(
    client: Any,
    player_ids: list[str],
    max_games_per_player: int | None = None,
    sleep_seconds: float = 0.2,
    verbose: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """
    Télécharge les parties brutes de chaque joueur retenu.

    Retour :
        {
            "player_id_1": [game_dict_1, game_dict_2, ...],
            ...
        }

    Remarque :
    cette fonction reste volontairement légère. Le filtrage scientifique
    sera fait plus tard sur le dataframe player_games.
    """
    out: dict[str, list[dict[str, Any]]] = {}

    for idx, player_id in enumerate(_normalize_player_ids(player_ids), start=1):
        games = _safe_export_rapid_rated_games(
            client=client,
            player_id=player_id,
            max_games=max_games_per_player,
        )
        out[player_id] = games

        if verbose:
            print(
                f"[Raw games] {idx}/{len(player_ids)} | {player_id} | "
                f"{len(games)} parties"
            )

        time.sleep(sleep_seconds)

    return out


# ============================================================================
# Expansion via adversaires
# ============================================================================

def _expand_once_via_opponents(
    client: Any,
    player_ids: list[str],
    max_games_per_player: int,
    sleep_seconds: float,
    verbose: bool,
) -> set[str]:
    opponents: set[str] = set()

    for idx, player_id in enumerate(player_ids, start=1):
        games = _safe_export_rapid_rated_games(
            client=client,
            player_id=player_id,
            max_games=max_games_per_player,
        )

        extracted = _extract_opponent_ids_from_games(games, focus_player_id=player_id)
        opponents |= extracted

        if verbose:
            print(
                f"[Expand] {idx}/{len(player_ids)} | {player_id} | "
                f"{len(games)} parties | {len(extracted)} adversaires uniques"
            )

        time.sleep(sleep_seconds)

    return opponents


def _extract_opponent_ids_from_games(
    games: list[dict[str, Any]],
    focus_player_id: str,
) -> set[str]:
    out: set[str] = set()
    focus = focus_player_id.lower()

    for game in games:
        players = game.get("players") or {}
        white = players.get("white") or {}
        black = players.get("black") or {}

        white_id = _extract_user_id(white)
        black_id = _extract_user_id(black)

        if white_id and white_id.lower() == focus and black_id:
            out.add(black_id)
        elif black_id and black_id.lower() == focus and white_id:
            out.add(white_id)

    return _normalize_player_ids(out)


# ============================================================================
# Préfiltrage
# ============================================================================

def _passes_light_prefilter(
    public_data: dict[str, Any] | None,
    rapid_perf: dict[str, Any] | None,
    config: CandidateSamplingConfig,
) -> bool:
    if public_data is None:
        return False

    if config.require_rapid_perf and rapid_perf is None:
        return False

    current_rating = _extract_current_rating(rapid_perf)

    if current_rating is None:
        return not config.require_rapid_perf

    return config.min_current_rapid_rating <= current_rating <= config.max_current_rapid_rating


# ============================================================================
# API wrappers
# ============================================================================

def _safe_get_public_data(client: Any, player_id: str) -> dict[str, Any] | None:
    try:
        return client.users.get_public_data(player_id)
    except Exception:
        return None


def _safe_get_rapid_performance(client: Any, player_id: str) -> dict[str, Any] | None:
    """
    Essaie plusieurs variantes raisonnables autour de get_user_performance,
    car selon les versions / wrappers, la signature exacte peut différer.
    """
    try:
        return client.users.get_user_performance(player_id, "rapid")
    except TypeError:
        pass
    except Exception:
        return None

    try:
        return client.users.get_user_performance(player_id, perf_type="rapid")
    except Exception:
        return None


def _safe_get_rating_history(client: Any, player_id: str) -> list[dict[str, Any]] | None:
    try:
        return client.users.get_rating_history(player_id)
    except Exception:
        return None


def _safe_export_rapid_rated_games(
    client: Any,
    player_id: str,
    max_games: int | None,
    since: int | None = None,
    until: int | None = None,
) -> list[dict[str, Any]]:
    try:
        kwargs = {
            "max": max_games,
            "perf_type": "rapid",
            "opening": True,
        }

        if since is not None:
            kwargs["since"] = since
        if until is not None:
            kwargs["until"] = until

        games = client.games.export_by_player(player_id, **kwargs)
        games = list(games)
        games = _local_filter_rapid_rated_finished_games(games)
        return games

    except Exception as e:
        print(f"[WARN] export_by_player failed for {player_id}: {e}")
        return []


# ============================================================================
# Parsing helpers
# ============================================================================

def _extract_current_rating(rapid_perf: dict[str, Any] | None) -> int | None:
    if not rapid_perf:
        return None

    # Cas 1 : réponse directement centrée sur la perf
    for key in ("rating", "prog"):
        value = rapid_perf.get(key)
        if key == "rating" and isinstance(value, (int, float)):
            return int(value)

    # Cas 2 : structure imbriquée
    perf = rapid_perf.get("perf")
    if isinstance(perf, dict):
        rating = perf.get("rating")
        if isinstance(rating, (int, float)):
            return int(rating)

    # Cas 3 : structure type public_data['perfs']['rapid']
    rapid = rapid_perf.get("rapid")
    if isinstance(rapid, dict):
        rating = rapid.get("rating")
        if isinstance(rating, (int, float)):
            return int(rating)

    return None


def _extract_user_id(player_blob: dict[str, Any]) -> str | None:
    if not isinstance(player_blob, dict):
        return None

    user = player_blob.get("user")
    if isinstance(user, dict):
        for key in ("id", "name", "username"):
            value = user.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    for key in ("id", "name", "username"):
        value = player_blob.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _local_filter_rapid_rated_finished_games(
    games: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for game in games:
        if not isinstance(game, dict):
            continue

        if game.get("rated") is not True:
            continue

        # Selon les payloads Lichess, perf / speed peuvent varier.
        speed = str(game.get("speed") or "").lower()
        perf = str(game.get("perf") or "").lower()

        if speed != "rapid" and perf != "rapid":
            continue

        status = str(game.get("status") or "").lower()
        if status in {"created", "started", ""}:
            continue

        out.append(game)

    return out


def _normalize_player_ids(player_ids: list[str] | set[str]) -> list[str]:
    cleaned: list[str] = []

    for player_id in player_ids:
        if not isinstance(player_id, str):
            continue
        value = player_id.strip()
        if not value:
            continue
        cleaned.append(value)

    # déduplication stable, insensible à la casse
    seen: set[str] = set()
    out: list[str] = []

    for value in cleaned:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)

    return out