import django
django.setup()


from musik_lib.collections.init import read_collection_file
from scripts import utility

import argparse


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file_names',
        type=str,
        nargs='+',
        help='space separated list of files under collection folder. Use file name only'
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

    for file_name in args.file_names:
        print("Reading file name %s" % file_name)
        collection = read_collection_file(file_name)
        utility.ingest_collection(collection)
        print("Done ingesting file name %s" % file_name)

    print("Finish DB ingest script")


if __name__ == '__main__':
    main()
