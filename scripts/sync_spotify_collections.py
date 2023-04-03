

import argparse

from integrations.spotify import spotify


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

    client = spotify.SpotifyClient.make_default()

    if args.clear:
        print("Removing local spotify collections")
        spotify.clear_local_collections()

    local_collections = spotify.get_local_collections_ids()
    remote_collections = spotify.get_remote_collections(
        client=client,
    )
    for collection in remote_collections:
        if collection.spotify_id in local_collections:
            print(f"Skipping existing collection : {collection.name}")
            continue
        spotify.write_collection(
            collection=collection,
        )
        print(f"New collection written : {collection.name}")

    print("Finish spotify ingest script")


if __name__ == '__main__':
    main()
