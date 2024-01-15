"""
playground for the client
"""

import argparse
from typing import Optional, Dict

import integrations.spotify.client



def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        action='store_true',
        help='when provided, all local collections will be deleted before sync. Default is false'
    )
    return parser.parse_args()


def search_for_track(client, track_name, artist_name, duration: str) -> Optional[Dict]:
    def duration_to_ms():
        duration_parts = duration.split(":")
        if len(duration_parts) != 2:
            raise ValueError(f"need to parse that -> {duration}")
        minutes, seconds = duration_parts
        return (
            int(minutes) * 60 + int(seconds)
        ) * 1000


    q = "&".join(
        [
            f"{track_name}",
            f"artist={artist_name}"
        ]
    )
    response = client.search(
        q=q,
        type="track",
    )
    items = response.get("tracks", {}).get("items")
    if not items:
        return None

    def find_item():
        origin_artists = artist_name.split(",")
        duration_in_ms = duration_to_ms()
        duration_min = duration_in_ms * 0.9
        duration_max = duration_in_ms * 1.1
        for item in items:
            if item["type"] != "track":
                continue
            artists_names_in_response = [
                a["name"] for a in item["artists"]
            ]
            for artist in origin_artists:
                if artist not in artists_names_in_response:
                    continue
            if not ( duration_min <= item["duration_ms"] <= duration_max):
                continue

            return item

    found_item = find_item()
    if not found_item:
        raise ValueError(
            "we did not find an item in response"
        )


def main():
    print("Start experiment")
    # args = read_args()

    # client = spotify.SpotifyClient.make_default()

    # if args.clear:
    #     print("Removing local spotify collections")
    #     spotify.clear_local_collections()

    client = integrations.spotify.client.SpotifyClient.make_default().client
    a = client.search(
        q='space&artist=David Bowie&type=track',
    )
    print(a)
    for item in a["tracks"]["items"]:
        for k, v in item.items():
            print(f"{k} = {v}")
        print("--")


    # for manual_collection_name in only_on_manual:
    #     ingest_collection(local_manual_collections[manual_collection_name])
    # for spotify_collection in  local_spotify_collections.values():
    #     ingest_spotify_collection(spotify_collection)

    print("Finish ingestion all collections")


if __name__ == '__main__':
    main()
