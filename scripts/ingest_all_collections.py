"""
Reads all local collections, including the ones from spotify ingestion
and gives priority to Spotify collections
"""

import django
django.setup()


from musik_lib import collections
from musik_lib.models.base import Library
from musik_lib.models.stats import LibraryStat
from scripts import utility

import argparse


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        action='store_true',
        help='when true, the db will be cleaned before ingesting the files. default is false'
    )
    return parser.parse_args()


def main():
    print("Start DB ingest script")
    args = read_args()

    if args.clear:
        print("Clearing DB")
        utility.clear_db()

    local_spotify_collections = collections.get_local_spotify_collections_by_name()
    print(f"Found {len(local_spotify_collections)} local spotify collections")

    local_manual_collections = collections.get_local_manual_collections_by_name()
    only_on_manual = set(local_manual_collections.keys()) - set(local_spotify_collections.keys())
    _ = Library.load()

    print("Reading first manual collections")
    for manual_collection_name in only_on_manual:
        print(f"Reading manual collection name {manual_collection_name}")
        collection = local_manual_collections[manual_collection_name]
        utility.ingest_collection(collection)

    # There is no concept of ordinal in spotify
    for spotify_collection in local_spotify_collections.values():
        print(f"Reading spotify collection name {spotify_collection['name']}")
        utility.ingest_spotify_collection(spotify_collection)

    l_stat = LibraryStat.load()
    print("Updating stats")
    l_stat.update()

    print("Finish DB ingest script")


if __name__ == '__main__':
    main()
