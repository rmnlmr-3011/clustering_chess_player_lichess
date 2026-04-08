# Code relatif à l'IO des données, notamment la sauvegarde et le chargement des parties brutes par joueur, ainsi que la construction du DataFrame player_games_raw à partir du dump brut API.


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.ingestion.build_player_games import build_player_games


def save_raw_games_for_one_player(
    player_id: str,
    games: list[dict[str, Any]],
    directory: str | Path,
) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{player_id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2, default=_json_default)

    return path



def load_raw_games_for_one_player(
    player_id: str,
    directory: str | Path,
) -> list[dict[str, Any]]:
    path = Path(directory) / f"{player_id}.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Le fichier {path} ne contient pas une liste de parties.")

    return data



def list_downloaded_player_ids(
    directory: str | Path,
) -> list[str]:
    directory = Path(directory)
    if not directory.exists():
        return []

    return sorted(p.stem for p in directory.glob("*.json"))


def load_raw_games_by_player_from_directory(
    directory: str | Path,
) -> dict[str, list[dict[str, Any]]]:
    directory = Path(directory)
    out: dict[str, list[dict[str, Any]]] = {}

    if not directory.exists():
        return out

    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"Le fichier {path} ne contient pas une liste de parties.")

        out[path.stem] = data

    return out




def save_raw_games_by_player(
    raw_games_by_player: dict[str, list[dict[str, Any]]],
    path: str | Path,
) -> None:
    """
    Sauvegarde les parties brutes par joueur au format JSON.

    Format attendu :
    {
        "player_id_1": [game_dict_1, game_dict_2, ...],
        "player_id_2": [...],
        ...
    }
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            raw_games_by_player,
            f,
            ensure_ascii=False,
            indent=2,
            default=_json_default,
        )


def load_raw_games_by_player(
    path: str | Path,
) -> dict[str, list[dict[str, Any]]]:
    """
    Recharge les parties brutes par joueur depuis un fichier JSON.
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Le contenu JSON chargé n'est pas un dict player_id -> list[games].")

    return data


def save_player_games_raw(
    df: pd.DataFrame,
    path: str | Path,
) -> None:
    """
    Sauvegarde un DataFrame player_games_raw au format JSON.

    Le fichier est stocké sous forme de liste de records :
    [
        {"col1": ..., "col2": ..., ...},
        ...
    ]

    Les datetime sont sérialisés en ISO 8601.
    Les NaN/NaT sont convertis en None.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    records = _dataframe_to_json_records(df)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            ensure_ascii=False,
            indent=2,
            default=_json_default,
        )


def load_player_games_raw(
    path: str | Path,
) -> pd.DataFrame:
    """
    Recharge un DataFrame player_games_raw depuis un fichier JSON.
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise ValueError("Le contenu JSON chargé pour player_games_raw n'est pas une liste de records.")

    df = pd.DataFrame(records)

    # Reparse des colonnes datetime si elles existent
    datetime_cols = [
        "datetime_utc",
    ]

    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    return df


# =====================================================================
# Helpers
# =====================================================================

def _dataframe_to_json_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    work = df.copy()

    # Conversion explicite des colonnes datetime en ISO 8601
    for col in work.columns:
        if pd.api.types.is_datetime64_any_dtype(work[col]):
            work[col] = work[col].apply(
                lambda x: x.isoformat() if pd.notna(x) else None
            )

    # Remplace NaN / NaT par None pour un JSON propre
    work = work.where(pd.notna(work), None)

    return work.to_dict(orient="records")


def _json_default(obj: Any) -> Any:
    """
    Convertisseur générique pour json.dump.
    """
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # numpy scalars éventuels
    try:
        import numpy as np

        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
    except Exception:
        pass

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def build_player_games_raw_from_api_dump(
    raw_games_by_player: dict[str, list[dict[str, Any]]],
) -> pd.DataFrame:
    """
    Construit le DataFrame player_games_raw à partir du dump brut API
    organisé par joueur.

    Étapes :
    - applique build_player_games(games) pour chaque joueur
    - concatène les DataFrames obtenus
    - supprime les doublons éventuels (player_id, game_id)

    Remarque :
    des doublons peuvent apparaître si une même partie a été téléchargée
    via plusieurs joueurs différents.
    """
    dfs: list[pd.DataFrame] = []

    for player_id, games in raw_games_by_player.items():
        if not games:
            continue

        df_player = build_player_games(games)

        if df_player.empty:
            continue

        dfs.append(df_player)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Suppression des doublons dus aux téléchargements croisés
    df = df.drop_duplicates(subset=["player_id", "game_id"]).reset_index(drop=True)

    return df


def save_player_games_selected(df, path):
    records = _dataframe_to_json_records(df)
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=_json_default)

def load_player_games_selected(path):
    with Path(path).open("r", encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    if "datetime_utc" in df.columns:
        df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], errors="coerce", utc=True)
    return df


