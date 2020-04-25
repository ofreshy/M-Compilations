from django.utils.dateparse import parse_duration

from musik_lib.models.stats import *


def get_track_artists(artist_field, artists_dict):
    artist_names = [a.strip() for a in artist_field.split("&")]
    artist_set = set()
    for artist_name in artist_names:
        if artist_name not in artists_dict:
            artist = Artist.objects.create(name=artist_name)
            artists_dict[artist_name] = artist
        artist_set.add(artists_dict[artist_name])
    return artist_set


def ingest_collection(d):
    collection, _ = Collection.objects.get_or_create(
        name=d["name"],
        nick_name=d["nick_name"],
        description=d["description"],
        created_year=d["created_year"],
        ordinal=d["ordinal"],
        library=Library.load()
    )

    # Safe to key by name as it is unique
    artists = dict(
        [(a.name, a) for a in Artist.objects.all()]
    )

    tracks = d["tracks"]
    for t in tracks:
        _, track = _get_or_create_track(t, artists)
        collection.track_set.add(track)
    collection.save()


def _get_or_create_track(track_dict, artist_dict):
    track_name = track_dict["name"].strip()
    track_artists = get_track_artists(track_dict["artist"], artist_dict)
    db_tracks = Track.objects.filter(name=track_name)

    if db_tracks:
        track_artists_ids = {a.id for a in track_artists}
        for track in db_tracks:
            db_track_set_id = {a.id for a in track.artist_set.all()}
            if db_track_set_id == track_artists_ids:
                # This is a duplicate track. return created=False, track
                return False, track

    duration_str = track_dict["duration"].strip()
    duration = parse_duration(duration_str)
    if duration is None:
        raise ValueError("Could not parse duration - '{}'n found in {}".format(duration_str, track_dict))

    track = Track.objects.create(
        name=track_name,
        duration=duration,
        released_year=track_dict["released_year"],
    )
    track.artist_set.add(*track_artists)
    track.save()
    # return created=True, track
    return True, track


def clear_db():
    Collection.objects.all().delete()
    Track.objects.all().delete()
    Artist.objects.all().delete()

    CollectionStat.objects.all().delete()
    LibraryStat.objects.all().delete()
