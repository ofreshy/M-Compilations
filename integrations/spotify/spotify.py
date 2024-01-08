"""
Ability to read the Spotify collections from remote
Using spotipy client

The client expects three env variables to be set
SPOTIPY_CLIENT_ID;
SPOTIPY_CLIENT_SECRET;
SPOTIPY_REDIRECT_URI=https://localhost:8080/callback
"""
import difflib
import json
import logging
import os.path
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

NUM_SEARCH_ITEMS = 5


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
    uri: str
    album: Dict

    @classmethod
    def from_spotify_api(cls, data: Dict):
        return cls(
            name=data["name"],
            spotify_id=data["id"],
            duration_ms=data["duration_ms"],
            artist=data["artists"],
            uri=data["uri"],
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
    def make_default(cls, limit=50, extra_scope=None):
        base_scope = [
            "user-read-private",
            "user-read-email",
            "user-library-read",
            "user-library-modify",
        ]
        extra_scope = extra_scope or []
        scope = base_scope + extra_scope
        return cls(
            client=spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope=scope,
                ),
            ),
            limit=limit,
        )

    def __init__(self, client: spotipy.Spotify, limit):
        self.client = client
        self.limit = limit

    def me(self):
        return self.client.me()

    def user_id(self):
        return self.me()["id"]

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

    def delete_from_saved_tracks(self, tracks: List[str]):
        """
        Takes a list of track ids or track urls
        """
        return self.client.current_user_saved_tracks_delete(
            tracks
        )

    def search_track(self, track_name, artist_name, duration: str) -> Optional[SpotifyTrack]:
        def gen_items():
            response = self.client.search(
                q=f"{track_name}, {artist_name}",
                type="track",
                limit=NUM_SEARCH_ITEMS,
            )
            items = response.get("tracks", {}).get("items", [])
            yield from (i for i in items)

        track_filter = make_track_filter(track_name, artist_name, duration)
        found_item = next(filter(track_filter, gen_items()), None)
        if not found_item:
            raise ValueError(
                f"Did not find a match for {track_name}, {artist_name} in items"
            )
        spotify_track = SpotifyTrack.from_spotify_api(found_item)
        print(
            f"Found a match for {track_name}, {artist_name} : {spotify_track}"
        )

        return spotify_track

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

    def create_playlist(self, playlist_name: str, uris: List[str], description: Optional[str]):
        """
        playlist name is unique in my collections so use this to understand whether this is a
        create or update
        """
        response = self.client.user_playlist_create(
            user=self.user_id(),
            name=playlist_name,
            description=description,
        )
        if response is None:
            raise

        response = self.client.playlist_add_items(
            playlist_id=response["id"],
            items=uris,
        )
        if response is None:
            raise

        return response

    def update_playlist(self, playlist_id: str, uris: List[str], collection: Dict):
        res = self.client.playlist_replace_items(
            playlist_id=playlist_id,
            items=uris,
        )
        if res is None:
            raise

        res = self.client.playlist_change_details(
            playlist_id=playlist_id,
            description=collection["description"],
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


def make_track_filter(track_name: str, artist_name: str, duration: str):
    def duration_to_ms():
        duration_parts = duration.split(":")
        len_duration = len(duration_parts)
        if len_duration == 3:
            hours, minutes, seconds = duration_parts
        elif len_duration == 2:
            hours, minutes, seconds = ['0'] + duration_parts
        else:
            raise ValueError(f"Failed to parse duration -> {duration}")

        return (
                int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        ) * 1000

    origin_artists = [a.strip() for a in artist_name.lower().split("&")]
    duration_in_ms = duration_to_ms()
    duration_min = duration_in_ms * 0.9
    duration_max = duration_in_ms * 1.1
    track_name_lower = track_name.lower()

    def type_filter(_item):
        if _item["type"] == "track":
            return True
        print(f"False. not type track item: {_item}")
        return False

    def similar_name_filter(_item) -> bool:
        item_name = _item["name"].lower()
        similar = difflib.SequenceMatcher(
            a=item_name,
            b=track_name_lower,
        ).ratio() > 0.9
        if similar:
            return True

        print(f"False. track name {track_name_lower} dissimilar to item name {item_name}")
        return False

    def artist_name_filter(_item):
        artists_names_in_response = [
            a["name"].lower() for a in _item["artists"]
        ]
        artist_in_response = any(
            [
                artist in artists_names_in_response
                for artist in origin_artists
            ]
        )
        if artist_in_response:
            return True
        print(
            f"False origin artist {origin_artists} in  {artists_names_in_response}"
        )
        return False

    def make_duration_filter(_item):
        if duration_min <= _item["duration_ms"] <= duration_max:
            return True
        print(
            f"False duration for {_item} is not in bounds ({duration_min}, {duration_max})"
        )
        return False

    all_filters = (
        type_filter,
        similar_name_filter,
        artist_name_filter,
        make_duration_filter,
    )

    def filter_all(_item):
        return all(
            [
                f(_item)
                for f
                in all_filters
            ]
        )

    return filter_all
