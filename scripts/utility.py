import re

from django.utils.dateparse import parse_duration

from musik_lib.models.stats import *

AND_REGEX = re.compile(" & | and ", re.IGNORECASE)
FEAT_REGEX = re.compile(" feat | featuring | feat\\. ", re.IGNORECASE)


def get_track_artists(artist_field, artists_dict):

    def normalize_artist_names(artist_names):
        return [
            name.strip().replace("\\&", "&")
            for name
            in AND_REGEX.split(artist_names)
        ]

    def get_normalized_names(artist_str):
        artist_names = list()
        if not artist_str:
            return artist_names
        artist_list = [a.strip() for a in normalize_artist_names(artist_str)]
        for artist_name in artist_list:
            artist_name = artist_name.strip()
            artist_obj, created = Artist.objects.get_or_create(name=artist_name)
            if created:
                artists_dict[artist_name] = artist_obj
            artist_names.append(artists_dict[artist_name])
        return artist_names

    featuring = FEAT_REGEX.search(artist_field)
    if featuring:
        artist_field = artist_field.replace(featuring.group(), " feat ")
    main_artists, _, feat_artists = artist_field.partition(" feat ")
    main_artists = get_normalized_names(main_artists)
    feat_artists = get_normalized_names(feat_artists)
    return main_artists, feat_artists


def ingest_collection(d):
    collection, created = Collection.objects.get_or_create(
        name=d["name"],
        nick_name=d["nick_name"],
        description=d["description"],
        created_year=d["created_year"],
        ordinal=d["ordinal"]
    )
    if not created:
        collection.trackincollection_set.all().delete()

    # Safe to key by name as it is unique
    artists = dict(
        [(a.name, a) for a in Artist.objects.all()]
    )

    tracks = [_get_or_create_track(t, artists)[1] for t in d["tracks"]]
    collection.add_tracks(tracks)
    collection.save()


def _get_or_create_track(track_dict, artist_dict):
    track_name = track_dict["name"].strip()
    main_artists, feat_artists = get_track_artists(track_dict["artist"], artist_dict)
    db_tracks = Track.objects.filter(name=track_name)

    if db_tracks:
        track_artists_ids = {a.id for a in (main_artists + feat_artists)}
        for track in db_tracks:
            db_track_set_id = {a.id for a in track.artists}
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
    track.artist.add(*main_artists)
    if feat_artists:
        track.featuring.add(*feat_artists)
    track.save()
    # return created=True, track
    return True, track


def clear_db():
    Track.objects.all().delete()
    Collection.objects.all().delete()
    Artist.objects.all().delete()
