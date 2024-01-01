"""
Ability to read the Spotify collections from remote
Using spotipy client

The client expects three env variables to be set
SPOTIPY_CLIENT_ID;
SPOTIPY_CLIENT_SECRET;
SPOTIPY_REDIRECT_URI=https://localhost:8080/callback
"""

import json
import os
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
                "album_group": data["album"].get("album_group"),
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
class SpotifyTrackFeatures:

    spotify_track_id: str
    track_name: str
    track_artists: List[Dict]

    audio_features: Dict

    version: str = "V0.0.1"

    @classmethod
    def from_spotify_api(cls, track: SpotifyTrack, audio_features: Dict):
        return cls(
            spotify_track_id=track.spotify_id,
            track_name=track.name,
            track_artists=track.artist,
            audio_features=audio_features,
        )


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
    def make_default(cls, limit=50):
        return cls(
            client=spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope=[
                        "user-read-private",
                        "user-read-email",
                        "user-library-read",
                        "user-library-modify"
                    ],
                ),
            ),
            limit=limit,
        )

    def __init__(self, client: spotipy.Spotify, limit):
        self.client = client
        self.limit = limit

    def me(self):
        return self.client.me()

    def saved_tracks(self):
        """
        Returns an iterator over saved tracks
        """
        def gen_items(saved_items):
            return (i["track"] for i in saved_items)

        response = self.client.current_user_saved_tracks(
            limit=self.limit,
        )
        while response["next"] is not None:
            yield from gen_items(response["items"])
            response = self.client.next(response)
        yield from gen_items(response["items"])

    def playlists(self) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items dict;
        Buffering the API call into chunks of items
        """
        def gen_items(playlist_items):
            return (i for i in playlist_items)

        playlists = self.client.user_playlists(
                user=self.me()["id"],
                limit=self.limit,
            )
        while playlists["next"] is not None:
            yield from gen_items(playlists["items"])
            playlists = self.client.next(playlists)
        yield from gen_items(playlists["items"])

    def playlist_items(self, playlist) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items (Tracks)
        """
        def gen_items(items):
            return (i for i in items)

        playlist_items = self.client.playlist_items(
            playlist_id=playlist["id"],
            limit=self.limit,
        )
        while playlist_items["next"] is not None:
            yield from gen_items(playlist_items["items"])
            playlist_items = self.client.next(playlist_items)
        yield from gen_items(playlist_items["items"])

    def audio_features(self, track_id: str):
        return self.client.audio_features(track_id)[0]


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
            or playlist_name.startswith("XXX") \
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
        playlist_items = list(client.playlist_items(playlist))
        try:
            yield SpotifyCollection.from_spotify_api(
                playlist=playlist,
                playlist_items=playlist_items,
            )
        except (KeyError, ValueError) as e:
            print(f"Error {e} in importing playlist : {playlist}")


def get_collection_stats(client: SpotifyClient, spotify_collection: SpotifyCollection) -> SpotifyCollectionStats:
    tracks_features = [
        SpotifyTrackFeatures.from_spotify_api(
            track=track,
            audio_features=client.audio_features(track.spotify_id),
        )
        for track in spotify_collection.tracks
    ]

    tracks_features = [
        SpotifyTrackFeatures.from_spotify_api(
            audio_features=client.audio_features(t.spotify_id),
            track=t,
        )
        for t in spotify_collection.tracks
    ]
    print(tracks_features)


def get_local_collections_ids(collection_path=SPOTIFY_COLLECTIONS_PATH) -> Set[str]:
    """
    Returns the collection ids that exists on collection_path
    """
    return {
        content["spotify_id"]
        for content
        in get_local_collections_content(collection_path)
    }


def get_local_collections_content(collection_path=SPOTIFY_COLLECTIONS_PATH) -> Iterator[dict]:
    def load_content(path: str):
        with open(path, "r") as f:
            return json.loads(f.read())

    return (
        load_content(os.path.join(collection_path, name))
        for name in os.listdir(collection_path)
        if name.endswith(".json")
    )


def get_local_collections_by_name(collection_path=SPOTIFY_COLLECTIONS_PATH) -> Dict[str, Dict]:
    """
    Returns all local collection content by their name
    """
    return {
        content["name"]: content
        for content
        in get_local_collections_content(collection_path)
    }


def clear_local_collections(path=SPOTIFY_COLLECTIONS_PATH):
    try:
        shutil.rmtree(path)
    except:
        pass
    else:
        os.makedirs(path)



# client = SpotifyClient.make_default(limit=20)
# # collections = get_remote_collections(client)
# # for col in collections:
# #     collection_stats = get_collection_stats(client, col)
# #     break
#
# cols = get_remote_collections(client)
# c = next(cols)
#
#
# a = get_collection_stats(client, c)
