"""
Needed this to recover a playlist that was deleted from the spotify UI

The UI is usually the ground truth, but here we use the lib as the ground truth to update the UI
since there is no way to recover a deleted playlist from the UI

"""
from typing import Dict

from integrations.spotify.client import SpotifyClient
from musik_lib import collections


def get_spotify_collections_to_sync(spotify_collection_names):
    local_spotify_collections = collections.get_local_spotify_collections_by_name()
    print(f"Found {len(local_spotify_collections)} local spotify collections")

    collections_to_sync = {
        name: col_content for name, col_content in local_spotify_collections.items()
        if name in spotify_collection_names
    }

    return collections_to_sync


def recover_collections(client: SpotifyClient, collections: Dict):
    playlist_name_to_id = {
        p["name"]: p["id"]
        for p in client.playlists()
    }

    def get_uri(track: Dict):
        if (uri := track.get("uri")) is not None:
            return uri
        return f"spotify:track:{track['spotify_id']}"

    for col_name, col_content in collections.items():
        if playlist_name_to_id.get(col_name):
            print(f"Error: Already have col name {col_name} on remote, cannot recover")
            continue

        tracks = [get_uri(track) for track in col_content['tracks']]
        if not tracks:
            print(f"Error: no tracks found in collection {col_name}")

        client.create_playlist(
            playlist_name=col_name,
            uris=tracks,
            description=col_content.get("description"),
        )
        print(f"Created playlist {col_name}")


def main():
    print("Start recovering collections")
    collection_names = [
        "To Ziv",
    ]
    cols = get_spotify_collections_to_sync(collection_names)
    if not cols:
        print("no collection to recover")
        return

    client = SpotifyClient.make_default(
        extra_scope=[
            "playlist-modify-public",
            "playlist-modify-private",
        ]
    )

    recover_collections(client, cols)

    print("Finish convert manual collection to spotify")


if __name__ == '__main__':
    main()
