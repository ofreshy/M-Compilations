"""
Ability to read the Spotify collections from remote
Using spotipy client

The client expects three env variables to be set


"""

import itertools
import json
import os.path
import shutil
from datetime import datetime
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass, asdict

from typing import List, Dict, Iterator, Set

BASE_PATH = Path(__file__).parent.absolute()
SPOTIFY_COLLECTIONS_PATH = os.path.join(
    BASE_PATH,
    "collections",
)


@dataclass
class SpotifyTrack:
    """
    Represent a track from the spotify API
    has a list of artists and an Album that we keep as a Dict for now
    """
    name: str
    spotify_id: str
    duration_ms: int
    artist: List[Dict]
    album: Dict

    @classmethod
    def from_spotify_api(cls, data: Dict):
        return cls(
            name=data["name"],
            spotify_id=data["id"],
            duration_ms=data["duration_ms"],
            artist=data["artists"],
            album={
                "album_name": data["album"]["name"],
                "album_group": data["album"]["album_group"],
                "album_type": data["album"]["album_type"],
                "released": data["album"]["release_date"],
                "spotify_id": data["album"]["id"],
            },
        )


@dataclass
class SpotifyCollection:
    """
    Represent a collection from the spotify API
    has a list of Spotify tracks
    """
    name: str
    spotify_id: str
    created_year: int | None
    description: str | None
    tracks: List[SpotifyTrack]

    @classmethod
    def from_spotify_api(cls, playlist: Dict, playlist_items: List):
        return cls(
            spotify_id=playlist["id"],
            name=playlist["name"],
            created_year=get_created_at_year(playlist_items),
            description=playlist["description"],
            tracks=[
                SpotifyTrack.from_spotify_api(pi["track"])
                for pi in playlist_items
            ],
        )


class SpotifyClient:
    """
    Thin wrapper for spotipy client
    so can get resources in a streaming fashion instead of bulk
    """
    client: spotipy.Spotify

    @classmethod
    def make_default(cls):
        return cls(
            client=spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope="user-read-private user-read-email",
                )
        )
    )

    def __init__(self, client: spotipy.Spotify):
        self.client = client

    def playlists(self) -> Iterator[Dict]:
        user_id = self.client.me()["id"]
        limit = 50

        def _get_playlists(offset):
            return self.client.user_playlists(
                user=user_id,
                offset=offset,
                limit=limit,
            )

        def _playlist_gen():
            offset = 0
            playlist = _get_playlists(offset)
            while playlist["next"] is not None:
                yield playlist["items"]
                offset += limit
                playlist = _get_playlists(offset)
            yield playlist["items"]

        for playlist in _playlist_gen():
            for item in playlist:
                yield item

    def playlist_items(self, playlist) -> Iterator[Dict]:
        playlist_id = playlist["id"]
        limit = 50

        def _get_items(offset):
            return self.client.playlist_items(
                playlist_id=playlist_id,
                offset=offset,
                limit=limit,
            )

        def _items_gen():
            offset = 0
            playlist_items = _get_items(offset)
            while playlist_items["next"] is not None:
                yield playlist_items["items"]
                offset += limit
                playlist_items = _get_items(offset)
            yield playlist_items["items"]

        return itertools.chain(*_items_gen())


def get_created_at_year(items):
    max_date = max(
        [
            i["added_at"] for i in items
        ]
    )
    return datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%SZ").year


def is_final_playlist(playlist: Dict) -> bool:
    """
    Returns True if playlist is finalized as some playlists are WIP
    """
    if playlist.get("owner", {}).get("display_name", "") != "ofreshy":
        return False

    playlist_name = playlist.get("name", "").upper()
    if playlist_name.startswith("ZZZ") \
            or playlist_name.startswith("KIDS") \
            or playlist_name.startswith("0"):
        return False

    return True


def write_collection(collection: SpotifyCollection,  prefix="", path=SPOTIFY_COLLECTIONS_PATH):
    if prefix:
        prefix += "-"
    with open(f"/{path}/{prefix}{collection.name}.json", "w") as f:
        f.write(
            json.dumps(
                asdict(collection),
                indent=4,
            )
        )


def get_remote_collections(client: SpotifyClient) -> Iterator[SpotifyCollection]:
    filtered_playlists = (p for p in client.playlists() if is_final_playlist(p))
    for playlist in filtered_playlists:
        yield SpotifyCollection.from_spotify_api(
            playlist=playlist,
            playlist_items=list(client.playlist_items(playlist)),
        )


def get_local_collections_ids(collection_path=SPOTIFY_COLLECTIONS_PATH) -> Set[str]:
    """
    Returns the collection ids that exists on collection_path
    """
    def get_collection_id(path: str):
        with open(path, "r") as f:
            collection = json.loads(f.read())
        return collection["spotify_id"]

    return {
        get_collection_id(
            path=os.path.join(collection_path, name)
        )
        for name in os.listdir(collection_path)
        if name.endswith(".json")
    }


def clear_local_collections(path=SPOTIFY_COLLECTIONS_PATH):
    try:
        shutil.rmtree(path)
    except:
        pass
    else:
        os.makedirs(path)



