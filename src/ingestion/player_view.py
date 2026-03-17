# Fonctions permettant de convertir une partie applatie en une partie du point de vue d'un joueur

from __future__ import annotations

from typing import Any


# Donne le résultat de la partie du point de vue d'un joueur (1.0 = victoire, 0.5 = nul, 0.0 = défaite)

def get_player_result(winner, color):

    if winner == "white":
        if color == "white":
            return 1.0
        else:
            return 0.0

    if winner == "black":
        if color == "black":
            return 1.0
        else:
            return 0.0

    return 0.5



# Transforme une partie aplatie en 2 rangées (1 par joueur).

def game_to_player_rows(flat_game: dict[str, Any]) -> list[dict[str, Any]]:

    rows = []

    for color in ("white", "black"):
        opponent_color = "black" if color == "white" else "white"

        row = {
            # Informations de la partie
            "game_id": flat_game["game_id"],
            "datetime_utc": flat_game["datetime_utc"],
            "weekday": flat_game["datetime_utc"].weekday(),


            # Informations des joueurs
            "player_id": flat_game[f"{color}_id"],
            "player_name": flat_game[f"{color}_name"],
            "opponent_id": flat_game[f"{opponent_color}_id"],
            "opponent_name": flat_game[f"{opponent_color}_name"],
            "color_player": color,

            # Informations des scores
            "result_player": get_player_result(flat_game.get("winner"), color),
            "elo_player_before": flat_game[f"{color}_rating_before"],
            "elo_player_after": flat_game[f"{color}_rating_after"],
            "elo_diff_player": flat_game[f"{color}_rating_diff"],

            # Détails de la partie
            "termination_type": flat_game["status"],
            "has_increment": flat_game["has_increment"],
            "opening_family": flat_game["opening_name"].split(":")[0] if flat_game["opening_name"] else None,
            "opening_eco": flat_game["opening_eco"],
            "opening_name": flat_game["opening_name"],
            "ply_count": flat_game["ply_count"],

            # Autres champs
            "perf": flat_game["perf"],
            "speed": flat_game["speed"],
            "rated": flat_game["rated"],
            "source": flat_game["source"],
        }

        rows.append(row)

    return rows