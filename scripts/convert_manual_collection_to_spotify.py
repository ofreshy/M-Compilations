"""
I aim to have all collections on spotify, even past collections that used to live on CD roms..
The songs appear in the manual collections and need to be mapped to spotify collections

The script here tries to find the matching tracks in Spotify and this is not a 1:1 mapping all the time,
so there are some fuzzy logic matchers


"""

from typing import Dict

from integrations.spotify.client import SpotifyClient
from musik_lib import collections


def get_manual_collections_to_sync():
    local_spotify_collections = collections.get_local_spotify_collections_by_name()
    print(f"Found {len(local_spotify_collections)} local spotify collections")

    local_manual_collections = collections.get_local_manual_collections_by_name()
    print(f"Found {len(local_manual_collections)} local manual collections")

    only_on_manual = {
        name: col_content for name, col_content in local_manual_collections.items()
        if name not in local_spotify_collections
    }

    return only_on_manual


def create_or_update_collections(client: SpotifyClient, collections: Dict):
    playlist_name_to_id = {
        p["name"]: p["id"]
        for p in client.playlists()
    }

    def find_tracks(collection: Dict):
        try:
            spotify_tracks = [
                client.search_track(track["name"], track["artist"], track["duration"])
                for track in collection["tracks"]
                # if track["name"].lower() == "empty boat"
            ]
        except ValueError as ve:
            print(f"Failed to convert collection {collection['name']}")
            print(ve)
            return None

        return [
            t.uri for t in spotify_tracks
        ]

    for col_name, col_content in collections.items():
        tracks = find_tracks(col_content)
        if tracks is None:
            break
        print("---------------------")

        playlist_name = col_content["name"]
        if (playlist_id := playlist_name_to_id.get(col_name)) is not None:
            client.update_playlist(
                playlist_id=playlist_id,
                uris=tracks,
                collection=col_content,
            )
            print(f"updated playlist : {playlist_name}")
        else:
            client.create_playlist(
                playlist_name=playlist_name,
                uris=tracks,
                description=col_content.get("description"),
            )
            print(f"Created playlist {playlist_name}")


def main():
    print("Start convert manual collection to spotify")

    only_on_manual = get_manual_collections_to_sync()
    if not only_on_manual:
        print("no collection left to convert")
        return
    skip_cols = {
        "My 2nd Album",  # missing international airport
        "To Assaf",  # missing im only sleeping from I am sam
        "Silence in the Studio",  # Did not find a match for Empty Boat, The Birdwatcher in items
        "The Cork",  # Did not find a match for Something New, The Dove in items
        "An Album",

    }
    cols = {
        n: c for n, c
        in only_on_manual.items()
        if n not in skip_cols
    }

    client = SpotifyClient.make_default(
        extra_scope=[
            "playlist-modify-public",
            "playlist-modify-private",
        ]
    )

    create_or_update_collections(client, cols)

    print("Finish convert manual collection to spotify")


if __name__ == '__main__':
    main()
