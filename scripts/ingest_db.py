import django
django.setup()


from musik_lib.collections.init import get_all_collection_files, read_collection_file
from musik_lib.models.base import Library
from scripts import utility

import argparse


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file_names',
        type=str,
        nargs='+',
        help='space separated list of files under collection folder.'
             ' Use file name only.'
             ' Or special argument all to read all collections'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='when true, the db will be cleaned before ingesting the files. default is false'
    )
    return parser


def main():
    print("Start DB ingest script")
    parser = setup_parser()
    args = parser.parse_args()

    if args.clear:
        print("Clearing DB")
        utility.clear_db()

    file_names = args.file_names
    if len(file_names) == 1 and args.file_names[0] == "all":
        file_names = get_all_collection_files()

    _ = Library.load()
    for file_name in file_names:
        print("Reading file name %s" % file_name)
        collection = read_collection_file(file_name)
        utility.ingest_collection(collection)
        print("Done ingesting file name %s" % file_name)

    print("Finish DB ingest script")


if __name__ == '__main__':
    main()
