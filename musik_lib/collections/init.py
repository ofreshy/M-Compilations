import json
import os

COLLECTION_DIR = os.path.dirname(os.path.realpath(__file__))


def read_collection_file(file_name):
    with open(os.path.join(COLLECTION_DIR, file_name)) as fp:
        return json.load(fp)
