from dotenv import load_dotenv
import os
import berserk

load_dotenv()

token = os.getenv("LICHESS_API_TOKEN")
if not token:
    raise ValueError("LICHESS_API_TOKEN introuvable dans .env")

session = berserk.TokenSession(token)
client = berserk.Client(session=session)

session = berserk.TokenSession(token)
client = berserk.Client(session=session)

account = client.account.get()
print(account)

