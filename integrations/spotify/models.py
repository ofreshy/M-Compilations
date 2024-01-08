"""
Ability to read the Spotify collections from remote
Using spotipy client

The client expects three env variables to be set
SPOTIPY_CLIENT_ID;
SPOTIPY_CLIENT_SECRET;
SPOTIPY_REDIRECT_URI=https://localhost:8080/callback
"""
from datetime import date, datetime

from dataclasses import dataclass

from typing import List, Dict, Optional


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


def get_created_at_date(items):
    max_date = max(
        [
            i["added_at"] for i in items
        ]
    )
    return datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%SZ").date()
