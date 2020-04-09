
import django
django.setup()

from musik_lib.models import *


def main():
    print("Start clearing DB")
    Collection.objects.all().delete()
    Track.objects.all().delete()
    Artist.objects.all().delete()
    print("Done clearing DB")


if __name__ == '__main__':
    main()
