

import argparse

from integrations.spotify import spotify
from musik_lib.collections.init import get_all_collection_files_by_name


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        action='store_true',
        help='when provided, all local collections will be deleted before sync. Default is false'
    )
    return parser.parse_args()


def main():
    print("Start add all local collections")
    # args = read_args()

    # client = spotify.SpotifyClient.make_default()

    # if args.clear:
    #     print("Removing local spotify collections")
    #     spotify.clear_local_collections()

    local_spotify_collections = spotify.get_local_collections_by_name()
    local_manual_collections = get_all_collection_files_by_name()
    only_on_manual = set(local_manual_collections.keys()) - set(local_spotify_collections.keys())
    print(f"local_spotify_collections len = {len(local_spotify_collections)}")
    print(f"local_manual_collections len = {len(local_manual_collections)}")
    print(f"only_on_manual len = {len(only_on_manual)}")

    ordered_spotify = list(sorted(list(local_spotify_collections.keys())))
    ordered_only = list(sorted(list(only_on_manual)))
    print(f"ordered_spotify keys = {ordered_spotify}")
    print(f"ordered_only keys = {ordered_only}")

    # for manual_collection_name in only_on_manual:
    #     ingest_collection(local_manual_collections[manual_collection_name])
    # for spotify_collection in  local_spotify_collections.values():
    #     ingest_spotify_collection(spotify_collection)


    print("Finish ingestino all collections")


if __name__ == '__main__':
    main()
