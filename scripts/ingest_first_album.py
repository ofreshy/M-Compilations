import django
django.setup()


from musik_lib.collections.init import read_collection_file
from scripts import utility


def main():
    print("Start")
    collection = read_collection_file("collection_1.json")
    utility.ingest_collection(collection)
    print("Finish")


if __name__ == '__main__':
    main()

