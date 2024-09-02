from pathlib import Path
from typing import Iterator, Dict, Optional

from integrations.spotify.client import SpotifyClient
from integrations.spotify.models import SpotifyCollection, SpotifyCollectionStats, SpotifyTrackFeatures

BASE_PATH = Path(__file__).parent.absolute()
SPOTIFY_COLLECTIONS_PATH = BASE_PATH.joinpath("collections")
UNFINISHED_PLAYLIST_PREFIXES = ("ZZZ", "KIDS", "XXX", "0")


def get_remote_collections(client: SpotifyClient) -> Iterator[SpotifyCollection]:
    display_name = client.me().get("display_name")
    if display_name is None:
        raise ValueError(
            f"display name is None in client_me response {client.me()}"
        )
    filtered_playlists = (p for p in client.playlists() if is_final_playlist(p, display_name))
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
    if _is_not_me_playlist(
            user_name=user_name,
            playlist_user=playlist.get("owner", {}).get("display_name", ""),
    ):
        return False

    if _is_unfinished_playlist(
        playlist_name=playlist.get("name", ""),
    ):
        return False

    return True


def _is_not_me_playlist(user_name: str, playlist_user: str) -> bool:
    return playlist_user != user_name


def _is_unfinished_playlist(playlist_name: str) -> bool:
    playlist_name = playlist_name.upper()
    unfinished = any(
        (
            playlist_name.startswith(p)
            for p in UNFINISHED_PLAYLIST_PREFIXES
        )
    )
    return unfinished
