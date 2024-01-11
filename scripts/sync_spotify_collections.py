import argparse

import integrations.spotify.client
import integrations.spotify.helpers
from musik_lib import collections


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        action='store_true',
        help='when provided, all local collections will be deleted before sync. Default is false'
    )
    return parser.parse_args()


def main():
    print("Start Spotify sync")
    args = read_args()

    client = integrations.spotify.client.SpotifyClient.make_default()

    if args.clear:
        print("Removing local spotify collections")
        collections.clear_spotify_local_collections()

    local_collections = collections.get_local_spotify_collection_ids()
    remote_collections = integrations.spotify.helpers.get_remote_collections(
        client=client,
    )
    number_of_new_written_collections = 0
    for collection in remote_collections:
        if collection.spotify_id in local_collections:
            print(f"Skipping existing collection : {collection.name}")
            continue
        collections.write_spotify_collection(
            collection=collection,
        )
        number_of_new_written_collections += 1
        print(f"New collection written : {collection.name}")

    if number_of_new_written_collections:
        print(f"Wrote {number_of_new_written_collections} of new collections ")
    else:
        print("No new collections written")

    print("Finish spotify ingest script")


if __name__ == '__main__':
    main()
