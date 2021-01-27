import os
import pathlib
from td.client import TDClient

REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_ID = os.getenv("TDAMERITRADE_CLIENT_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")

if not CREDENTIALS_PATH:
    credentials_path = str(pathlib.Path(__file__).parent) + "/credentials.json"
    os.putenv("CREDENTIALS_PATH", credentials_path)


session = TDClient(
    client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, credentials_path=CREDENTIALS_PATH,
)
session.login()
