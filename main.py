import os
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from fastapi import FastAPI, status, Response
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPE = os.getenv('SCOPE')
REDIRECT_URI = os.getenv('REDIRECT_URI')
NOTEBOOK_ID = os.getenv('NOTEBOOK_ID')
IPHONE_ID = os.getenv('IPHONE_ID')

app = FastAPI()

auth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPE,
    redirect_uri=REDIRECT_URI
)

sp = spotipy.Spotify(auth_manager=auth)

devices = {"notebook": NOTEBOOK_ID, "iphone": IPHONE_ID}


@app.get("/")
def index():
    return [
        {"name": "devices", "uri": "/devices", "method": "GET"},
        {"name": "play", "uri": "/play?music_id=<id>&target=<device_name>", "method": "POST"}
    ]


@app.get("/devices", status_code=status.HTTP_200_OK)
def read_root():
    data = sp.devices()
    return data['devices']


@app.post("/play")
def read_item(response: Response, music_id: str | None = None, target: str | None = None):
    try:
        device_id = devices[target]
        track = f"spotify:track:{music_id}"

        sp.transfer_playback(device_id=device_id)
        sp.start_playback(device_id=device_id, uris=[track])

        return {"status": "playing", "device": target}
    except SpotifyException as err:
        error_msg = f"Error trying to play music | {err}"
        logging.error(error_msg)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": error_msg}
    except KeyError:
        error_msg = f"Device: {target} not found"
        logging.error(error_msg)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": error_msg}
