"""
Ability to read the Spotify collections from remote
Using spotipy client

The client expects three env variables to be set


"""

import itertools
import json
import os.path
import shutil
from datetime import date, datetime
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass, asdict

from typing import List, Dict, Iterator, Optional, Set

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
    created_date: date | None
    description: str | None
    tracks: List[SpotifyTrack]

    @classmethod
    def from_spotify_api(cls, playlist: Dict, playlist_items: List):
        return cls(
            spotify_id=playlist["id"],
            name=playlist["name"],
            created_date=get_created_at_date(playlist_items),
            description=playlist["description"],
            tracks=[
                SpotifyTrack.from_spotify_api(pi["track"])
                for pi in playlist_items
            ],
        )

    @property
    def track_ids(self) -> List[str]:
        """
        Returns list of spotify ids for current tracks
        """
        return [t.spotify_id for t in self.tracks]


@dataclass
class SpotifyTrackStats:
    @classmethod
    def from_spotify_api(cls, audio_features: Dict):
        return cls()


@dataclass
class SpotifyCollectionStats:
    @classmethod
    def from_spotify_api(cls, audio_features: Dict):
        return cls()


class SpotifyClient:
    """
    Thin wrapper for spotipy client
    so can get resources in a streaming fashion instead of bulk
    """
    client: spotipy.Spotify
    limit: int

    @classmethod
    def make_default(cls):
        return cls(
            client=spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope="user-read-private user-read-email",
                ),
            ),
            limit=50,
        )

    def __init__(self, client: spotipy.Spotify, limit):
        self.client = client
        self.limit = limit

    def me(self):
        return self.client.me()

    def playlists(self) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items dict;
        Buffering the API call into chunks of items
        """
        user_id = self.me()["id"]
        limit = self.limit

        def _get_playlists(offset):
            return self.client.user_playlists(
                user=user_id,
                offset=offset,
                limit=limit,
            )

        def _playlist_gen():
            offset = 0
            playlists = _get_playlists(offset)
            while playlists["next"] is not None:
                yield playlists["items"]
                offset += limit
                playlists = _get_playlists(offset)
            yield playlists["items"]

        for playlist in _playlist_gen():
            for item in playlist:
                yield item

    def playlist_items(self, playlist) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items (Tracks)
        """
        playlist_id = playlist["id"]
        limit = self.limit

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

    def get_track_stats(self, spotify_track_id: str):
        """
        Given spotify track id, returns the stats associated with the track
        """
        return self.client.audio_analysis(spotify_track_id)

    def get_collection_features(self, collection: SpotifyCollection):
        return self.client.audio_features(
                tracks=[
                    t.spotify_id for t in collection.tracks
                ]
            )


def get_created_at_date(items):
    max_date = max(
        [
            i["added_at"] for i in items
        ]
    )
    return datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%SZ").date()


def is_final_playlist(playlist: Dict, user_name: Optional[str] = None) -> bool:
    """
    Returns True if playlist is finalized as some playlists are WIP
    """
    if user_name is not None:
        playlist_user = playlist.get("owner", {}).get("display_name", "")
        if playlist_user != user_name:
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
                default=str,
            )
        )


def get_remote_collections(client: SpotifyClient) -> Iterator[SpotifyCollection]:
    user_name = client.me().get("user_name")
    filtered_playlists = (p for p in client.playlists() if is_final_playlist(p, user_name))
    for playlist in filtered_playlists:
        yield SpotifyCollection.from_spotify_api(
            playlist=playlist,
            playlist_items=list(client.playlist_items(playlist)),
        )


def get_collection_stats(client: SpotifyClient, spotify_collection: SpotifyCollection) -> SpotifyCollectionStats:
    tracks_features = [
        client.get_track_stats(tid)
        for tid in spotify_collection.track_ids
    ]
    collection_features = client.get_collection_features(spotify_collection)
    return print()
    # return SpotifyCollectionStats(
    #     track_features=
    # )


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



client = SpotifyClient.make_default()
collections = get_remote_collections(client)
for col in collections:
    collection_stats = get_collection_stats(client, col)
    break
