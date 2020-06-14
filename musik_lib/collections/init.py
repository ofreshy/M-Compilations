import json
import os

COLLECTION_DIR = os.path.dirname(os.path.realpath(__file__))
COLLECTION_FILES = sorted([f for f in os.listdir(COLLECTION_DIR) if f.startswith("collection_")])

def read_collection_file(file_name):
    with open(os.path.join(COLLECTION_DIR, file_name)) as fp:
        return json.load(fp)

def get_all_collection_files():
    return COLLECTION_FILES

def resolve_collection_file(file_name_prefix):
    full_file_names = [f for f in COLLECTION_FILES if f.startswith(file_name_prefix)]
    if not full_file_names:
        raise ValueError("No file name with prefix '%s' found in '%s'" % (file_name_prefix, ",".join(COLLECTION_FILES)))
    elif len(full_file_names) > 1:
        raise ValueError("Ambiguous file name with prefix '%s', found following files '%s'" % (file_name_prefix, ",".join(full_file_names)))
    else:
        return full_file_names[0]
