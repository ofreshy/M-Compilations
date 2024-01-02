import django

django.setup()

from musik_lib.collections.__init__ import get_local_manual_collection_file_names, read_manual_collection_file, \
    resolve_manual_collection_files
from musik_lib.models.base import Library
from musik_lib.models.stats import LibraryStat
from scripts import utility

import argparse


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'collection_numbers',
        type=str,
        nargs='+',
        help='space separated list of collection numbers under collection folder.'
             ' Use file numbers only, e.g. "10 40" for collection_10, collection_40 respectively'
             ' Duplicate numbers will be ignored.'
             ' If no respective collection is found then an error is raised'
             ' Use special argument "all" to read all collections'
    )
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

    collection_numbers = args.collection_numbers
    if len(collection_numbers) == 1 and args.collection_numbers[0] == "all":
        file_names = get_local_manual_collection_file_names()
    else:
        file_names = resolve_manual_collection_files(collection_numbers)

    _ = Library.load()
    for file_name in file_names:
        print("Reading file name %s" % file_name)
        collection = read_manual_collection_file(file_name)
        utility.ingest_collection(collection)
        print("Done ingesting file name %s" % file_name)

    l_stat = LibraryStat.load()
    print("Updating stats")
    l_stat.update()

    print("Finish DB ingest script")


if __name__ == '__main__':
    main()
