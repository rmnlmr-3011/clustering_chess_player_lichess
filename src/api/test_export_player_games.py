from dotenv import load_dotenv
import os
import berserk
from pprint import pprint

load_dotenv()

token = os.getenv("LICHESS_API_TOKEN")
if not token:
    raise ValueError("LICHESS_API_TOKEN introuvable dans .env")

session = berserk.TokenSession(token)
client = berserk.Client(session=session)

username = "farqin2121"  # joueur test, à remplacer si besoin

games = client.games.export_by_player(
    username,
    max=5,
    perf_type="rapid",
    clocks=True,
    opening=True,
)

games = list(games)

print(f"{len(games)} parties récupérées")

if games:
    pprint(games[0])

    