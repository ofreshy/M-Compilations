import os
from pathlib import Path
from typing import Iterator, Dict, Optional

from integrations.spotify.client import SpotifyClient
from integrations.spotify.models import SpotifyCollection, SpotifyCollectionStats, SpotifyTrackFeatures


BASE_PATH = Path(__file__).parent.absolute()
SPOTIFY_COLLECTIONS_PATH = BASE_PATH.joinpath("collections")


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
