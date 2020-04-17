from django.utils.dateparse import parse_duration

from musik_lib.models.base import *


def get_artists_from_db():
    return dict(
        [(a.name, a) for a in Artist.objects.all()]
    )


def get_track_artists(artist_field, artists_dict):
    artist_names = [a.strip() for a in artist_field.split("&")]
    artist_set = set()
    for artist_name in artist_names:
        if artist_name not in artists_dict:
            artist = Artist(name=artist_name)
            artist.save()
            artists_dict[artist_name] = artist
        artist_set.add(artists_dict[artist_name])
    return artist_set


def ingest_collection(d):
    collection = Collection(
        name=d["name"],
        nick_name=d["nick_name"],
        description=d["description"],
        created_year=d["created_year"],
        ordinal=d["ordinal"],
        library=Library.load()
    )

    collection.save()

    artists = get_artists_from_db()

    tracks = d["tracks"]
    for t in tracks:
        track = Track(
            name=t["name"].strip(),
            duration=parse_duration(t["duration"].strip()),
            released_year=t["released_year"],
        )
        track.save()

        track_artists = get_track_artists(t["artist"], artists)
        for track_artist in track_artists:
            track.artist_set.add(track_artist)

        track.save()

        collection.track_set.add(track)

    collection.save()


def clear_db():
    Collection.objects.all().delete()
    Track.objects.all().delete()
    Artist.objects.all().delete()
