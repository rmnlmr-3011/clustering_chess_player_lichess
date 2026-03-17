# Fonction permettant de convertir una partie brute en une structure plate

def flatten_game(game: dict) -> dict:
    white = game.get("players", {}).get("white", {})
    black = game.get("players", {}).get("black", {})
    opening = game.get("opening", {})
    clock = game.get("clock", {})
    moves_str = game.get("moves", "")

    white_rating = white.get("rating")
    black_rating = black.get("rating")
    white_rating_diff = white.get("ratingDiff")
    black_rating_diff = black.get("ratingDiff")

    return {
        "game_id": game.get("id"),
        "datetime_utc": game.get("createdAt"),
        "perf": game.get("perf"),
        "speed": game.get("speed"),
        "rated": game.get("rated"),
        "source": game.get("source"),
        "status": game.get("status"),
        "winner": game.get("winner"),

        "white_id": white.get("user", {}).get("id"),
        "white_name": white.get("user", {}).get("name"),
        "black_id": black.get("user", {}).get("id"),
        "black_name": black.get("user", {}).get("name"),

        "white_rating_before": white_rating,
        "black_rating_before": black_rating,
        "white_rating_diff": white_rating_diff,
        "black_rating_diff": black_rating_diff,

        "white_rating_after": (
            white_rating + white_rating_diff
            if white_rating is not None and white_rating_diff is not None
            else None
        ),
        "black_rating_after": (
            black_rating + black_rating_diff
            if black_rating is not None and black_rating_diff is not None
            else None
        ),

        "opening_eco": opening.get("eco"),
        "opening_name": opening.get("name"),

        "clock_initial": clock.get("initial"),
        "clock_increment": clock.get("increment"),
        "has_increment": int((clock.get("increment") or 0) > 0),

        "moves": moves_str,
        "ply_count": len(moves_str.split()) if moves_str else 0,
    }
    