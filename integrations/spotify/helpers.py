import json
from dataclasses import asdict
from typing import Iterator

from integrations.spotify.client import SpotifyClient
from integrations.spotify.models import SpotifyCollection, SPOTIFY_COLLECTIONS_PATH, is_final_playlist, \
    SpotifyCollectionStats, SpotifyTrackFeatures


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
