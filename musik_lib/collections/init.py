import json
import os

COLLECTION_DIR = os.path.dirname(os.path.realpath(__file__))


def read_collection_file(file_name):
    with open(os.path.join(COLLECTION_DIR, file_name)) as fp:
        return json.load(fp)


def get_all_collection_files():
    return sorted(
        [f for f in os.listdir(COLLECTION_DIR) if f.startswith("collection_")]
    )
