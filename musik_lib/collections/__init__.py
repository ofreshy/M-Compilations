import json
import os
import shutil

from collections import OrderedDict
from typing import Set, Iterator, Dict

COLLECTION_PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
MANUAL_COLLECTION_DIR = os.path.join(COLLECTION_PARENT_DIR, "from_manual")
SPOTIFY_COLLECTION_DIR = os.path.join(COLLECTION_PARENT_DIR, "from_spotify")
MANUAL_COLLECTION_FILE_NAMES = OrderedDict(
    [
        (f.split("_")[1], f)
        for f
        in sorted(
            [
                f for f in os.listdir(MANUAL_COLLECTION_DIR) if f.startswith("collection_")
            ]
        )
    ]
)

SPOTIFY_COLLECTIONS_FILE_NAMES = [
    name
    for name in os.listdir(SPOTIFY_COLLECTION_DIR)
    if name.endswith(".json")
]


def _load_json_file(file_path):
    with open(file_path) as fp:
        return json.load(fp)


def read_manual_collection_file(file_name):
    return _load_json_file(
        os.path.join(MANUAL_COLLECTION_DIR, file_name)
    )


def read_spotify_collection_file(file_name):
    return _load_json_file(
        os.path.join(SPOTIFY_COLLECTION_DIR, file_name)
    )


def get_local_manual_collection_file_names():
    return MANUAL_COLLECTION_FILE_NAMES.values()


def get_local_manual_collections_by_name() -> Dict[str, Dict]:
    collection_files = get_local_manual_collection_file_names()
    collection_contents = (
        read_manual_collection_file(f)
        for f in collection_files
    )
    return {
        content["name"]: content for content in collection_contents
    }


def resolve_manual_collection_files(collection_numbers):
    # dedup the collection numbers while also keeping their order
    collection_numbers_dedup = OrderedDict([(cn, cn) for cn in collection_numbers]).keys()
    missing_collections = collection_numbers_dedup - MANUAL_COLLECTION_FILE_NAMES.keys()
    if missing_collections:
        raise ValueError("Collection files for numbers '%s' do not exist" % (",".join(collection_numbers_dedup)))
    return [MANUAL_COLLECTION_FILE_NAMES[cn] for cn in collection_numbers_dedup]


def get_local_spotify_collection_ids() -> Set[str]:
    """
    Returns the collection ids that exists on collection_path
    """
    return {
        content["spotify_id"]
        for content
        in get_local_spotify_collections_content()
    }


def get_local_spotify_collections_content() -> Iterator[dict]:
    return (
        _load_json_file(os.path.join(SPOTIFY_COLLECTION_DIR, name))
        for name in SPOTIFY_COLLECTIONS_FILE_NAMES
    )


def get_local_spotify_collections_by_name() -> Dict[str, Dict]:
    """
    Returns all local collection content by their name
    """
    return {
        content["name"]: content
        for content
        in get_local_spotify_collections_content()
    }


def clear_spotify_local_collections():
    try:
        shutil.rmtree(SPOTIFY_COLLECTION_DIR)
    except:
        pass
    else:
        os.makedirs(SPOTIFY_COLLECTION_DIR)
