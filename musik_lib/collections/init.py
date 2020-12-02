import json
import os

from collections import OrderedDict

COLLECTION_DIR = os.path.dirname(os.path.realpath(__file__))
COLLECTION_DICT = OrderedDict(
    [
        (f.split("_")[1], f)
        for f
        in sorted([f for f in os.listdir(COLLECTION_DIR) if f.startswith("collection_")])
    ]
)


def read_collection_file(file_name):
    with open(os.path.join(COLLECTION_DIR, file_name)) as fp:
        return json.load(fp)


def get_all_collection_files():
    return COLLECTION_DICT.values()


def resolve_collection_files(collection_numbers):
    missing_collections =  set(collection_numbers) - COLLECTION_DICT.keys()
    if missing_collections:
        raise ValueError("Collection files for numbers '%s' do not exist" % (",".join(collection_numbers)))
    return [COLLECTION_DICT[cn] for cn in collection_numbers]
