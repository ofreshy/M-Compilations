from datetime import timedelta

from musik_lib.models.stats import *


def library():
    return Library.load()


def library_stat():
    return LibraryStat.objects.get_or_create(library=Library.load())[0]


def artist_1(name="A1"):
    return Artist.objects.get_or_create(name=name)[0]


def artist_2(name="A2"):
    return Artist.objects.get_or_create(name=name)[0]


def artist_3(name="A3"):
    return Artist.objects.get_or_create(name=name)[0]


def track_1(name="Track1", duration=timedelta(minutes=6, seconds=18), released_year=2000):
    return Track.objects.get_or_create(
            name=name,
            duration=duration,
            released_year=released_year,
    )[0]


def track_2(name="Track2", duration=timedelta(minutes=2, seconds=0), released_year=1979):
    return Track.objects.get_or_create(
            name=name,
            duration=duration,
            released_year=released_year,
    )[0]


def track_3(name="Track3", duration=timedelta(minutes=5, seconds=13), released_year=2020):
    return Track.objects.get_or_create(
        name=name,
        duration=duration,
        released_year=released_year,
    )[0]


def collection_1(name="C1", nick_name="C1 nick", description="C1 description", released_year=2000, ordinal=1, lib=None):
    return Collection.objects.get_or_create(
        name=name,
        nick_name=nick_name,
        description=description,
        created_year=released_year,
        ordinal=ordinal,
        library=lib or library()
    )[0]


def collection_2(name="C2", nick_name="C2 nick", description="C2 description", released_year=2010, ordinal=2, lib=None):
    return Collection.objects.get_or_create(
        name=name,
        nick_name=nick_name,
        description=description,
        created_year=released_year,
        ordinal=ordinal,
        library=lib or library()
    )[0]


def collection_stat(collection=None, lib_stat=None):
    return CollectionStat.objects.get_or_create(
            collection=collection or collection_1(),
            library_stat=lib_stat or library_stat(),
    )[0]
