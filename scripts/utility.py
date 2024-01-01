import re

from django.utils.dateparse import parse_duration

from musik_lib.models.stats import *

AND_REGEX = re.compile(" & | and |, ", re.IGNORECASE)
FEAT_REGEX = re.compile(" feat | featuring | feat\\. | מארח את", re.IGNORECASE)


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


def ingest_spotify_collection(d):
    """
    {'name': 'Zeitgeist 2020 I - Israeli', 'spotify_id': '4bnPt3UfMQl4ktXiWEMhNx', 'created_date': '2021-06-12', 'description': 'Playlist Created with https:&#x2F;&#x2F;www.tunemymusic.com?source=plcreateds that lets you transfer your playlist to Spotify from any music platform such as YouTube, Deezer etc',
    'tracks': [{'name': 'מדינה מחלה', 'spotify_id': '4RMwG3ejKu9XUV1mOFQWXs', 'duration_ms': 76106, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/2YLRhPggvGSfODSnpF1Omq'}, 'href': 'https://api.spotify.com/v1/artists/2YLRhPggvGSfODSnpF1Omq', 'id': '2YLRhPggvGSfODSnpF1Omq', 'name': 'Tabarnak', 'type': 'artist', 'uri': 'spotify:artist:2YLRhPggvGSfODSnpF1Omq'}], 'album': {'album_name': 'טברנק שרים טברנק', 'album_group': None, 'album_type': 'album', 'released': '2020-01-12', 'spotify_id': '2WWJUIuNJO8D3yPgQIxZPj'}}, {'name': 'הארץ השטוחה', 'spotify_id': '4o2nL7ptRcPfj3q8Zd4b3t', 'duration_ms': 160373, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/4p3CuBU6qQdQgIqec3hooj'}, 'href': 'https://api.spotify.com/v1/artists/4p3CuBU6qQdQgIqec3hooj', 'id': '4p3CuBU6qQdQgIqec3hooj', 'name': "Haze'evot", 'type': 'artist', 'uri': 'spotify:artist:4p3CuBU6qQdQgIqec3hooj'}], 'album': {'album_name': 'הארץ השטוחה', 'album_group': None, 'album_type': 'album', 'released': '2020-02-04', 'spotify_id': '1mHowwNjZbUgHu5OAM4x8v'}}, {'name': 'בתחנה המרכזית החדשה', 'spotify_id': '0Y49XkW5IxcpXQITnsndSq', 'duration_ms': 281658, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/4j3lS6XL3cIyv2VSHglQKv'}, 'href': 'https://api.spotify.com/v1/artists/4j3lS6XL3cIyv2VSHglQKv', 'id': '4j3lS6XL3cIyv2VSHglQKv', 'name': 'קוסטה קפלן', 'type': 'artist', 'uri': 'spotify:artist:4j3lS6XL3cIyv2VSHglQKv'}], 'album': {'album_name': 'בתחנה המרכזית החדשה', 'album_group': None, 'album_type': 'single', 'released': '2019-12-12', 'spotify_id': '2Qw62oSycTRZ55cE2iuG7y'}}, {'name': 'לילה של רוק טיפתי', 'spotify_id': '4b4MvL2CUJhK3qe41wRaIf', 'duration_ms': 183164, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/5z1KOeWbVsTbF7GtxDvXAV'}, 'href': 'https://api.spotify.com/v1/artists/5z1KOeWbVsTbF7GtxDvXAV', 'id': '5z1KOeWbVsTbF7GtxDvXAV', 'name': 'Aviv Mark', 'type': 'artist', 'uri': 'spotify:artist:5z1KOeWbVsTbF7GtxDvXAV'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/768G5Kcqh3hCU1NK2I1ofx'}, 'href': 'https://api.spotify.com/v1/artists/768G5Kcqh3hCU1NK2I1ofx', 'id': '768G5Kcqh3hCU1NK2I1ofx', 'name': 'The Crotches', 'type': 'artist', 'uri': 'spotify:artist:768G5Kcqh3hCU1NK2I1ofx'}], 'album': {'album_name': 'לילה של רוק טיפתי', 'album_group': None, 'album_type': 'single', 'released': '2020-09-06', 'spotify_id': '6tR7rC6d80PhTx4uMeulQk'}}, {'name': 'מסיבה', 'spotify_id': '6wp8MFCXy2U6hAoLGnlxJn', 'duration_ms': 202171, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/3cDi1D2FHMVgljfdB1QVgr'}, 'href': 'https://api.spotify.com/v1/artists/3cDi1D2FHMVgljfdB1QVgr', 'id': '3cDi1D2FHMVgljfdB1QVgr', 'name': 'Jasmin Moallem', 'type': 'artist', 'uri': 'spotify:artist:3cDi1D2FHMVgljfdB1QVgr'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/4XRymSxqMfKCkA6njs39lM'}, 'href': 'https://api.spotify.com/v1/artists/4XRymSxqMfKCkA6njs39lM', 'id': '4XRymSxqMfKCkA6njs39lM', 'name': 'Shekel', 'type': 'artist', 'uri': 'spotify:artist:4XRymSxqMfKCkA6njs39lM'}], 'album': {'album_name': 'אריה', 'album_group': None, 'album_type': 'album', 'released': '2020-02-27', 'spotify_id': '0605dh7Wm1z9kZuTwnurMJ'}}, {'name': 'אגו טריפ', 'spotify_id': '3vqPeOETjedoo2w8UUB34o', 'duration_ms': 113093, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/2DMdTMjbXXHnlhsnJ9UJyz'}, 'href': 'https://api.spotify.com/v1/artists/2DMdTMjbXXHnlhsnJ9UJyz', 'id': '2DMdTMjbXXHnlhsnJ9UJyz', 'name': 'Sima Noon', 'type': 'artist', 'uri': 'spotify:artist:2DMdTMjbXXHnlhsnJ9UJyz'}], 'album': {'album_name': 'תדברי כבר', 'album_group': None, 'album_type': 'album', 'released': '2020-02-13', 'spotify_id': '6Crmzlf2yUkeomvVibhy6L'}}, {'name': 'זבוב צרפתי', 'spotify_id': '4jlAGIYvVx9iO1sKTvBgTd', 'duration_ms': 111111, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/2EBTjku8UEjCoVEhWaBEuv'}, 'href': 'https://api.spotify.com/v1/artists/2EBTjku8UEjCoVEhWaBEuv', 'id': '2EBTjku8UEjCoVEhWaBEuv', 'name': 'כרמלה והאורחים הנוספים', 'type': 'artist', 'uri': 'spotify:artist:2EBTjku8UEjCoVEhWaBEuv'}], 'album': {'album_name': 'מיקסטייפ נדירים בדוק', 'album_group': None, 'album_type': 'album', 'released': '2020-03-01', 'spotify_id': '43fq976ogvyXDzqC3tEseJ'}}, {'name': 'זה בדם שלי', 'spotify_id': '0xbaqIFDysDetqbKfdYn8N', 'duration_ms': 169412, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/1SOCXWLgBvXDqNobiSnGM7'}, 'href': 'https://api.spotify.com/v1/artists/1SOCXWLgBvXDqNobiSnGM7', 'id': '1SOCXWLgBvXDqNobiSnGM7', 'name': 'Teddy Neguse', 'type': 'artist', 'uri': 'spotify:artist:1SOCXWLgBvXDqNobiSnGM7'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/3cDi1D2FHMVgljfdB1QVgr'}, 'href': 'https://api.spotify.com/v1/artists/3cDi1D2FHMVgljfdB1QVgr', 'id': '3cDi1D2FHMVgljfdB1QVgr', 'name': 'Jasmin Moallem', 'type': 'artist', 'uri': 'spotify:artist:3cDi1D2FHMVgljfdB1QVgr'}], 'album': {'album_name': 'זה בדם שלי', 'album_group': None, 'album_type': 'single', 'released': '2020-08-31', 'spotify_id': '5aDebq86Xeh2XeNjPWfAE4'}}, {'name': 'VIEWS', 'spotify_id': '2RmuZoZ3nsICUu7GsLDHW9', 'duration_ms': 165861, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/5VwCIS8jdx9ZHjApLFNrTZ'}, 'href': 'https://api.spotify.com/v1/artists/5VwCIS8jdx9ZHjApLFNrTZ', 'id': '5VwCIS8jdx9ZHjApLFNrTZ', 'name': 'Noga Erez', 'type': 'artist', 'uri': 'spotify:artist:5VwCIS8jdx9ZHjApLFNrTZ'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/08v1r0jqDyvSo2LtSqHxcy'}, 'href': 'https://api.spotify.com/v1/artists/08v1r0jqDyvSo2LtSqHxcy', 'id': '08v1r0jqDyvSo2LtSqHxcy', 'name': 'Reo Cragun', 'type': 'artist', 'uri': 'spotify:artist:08v1r0jqDyvSo2LtSqHxcy'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/0B0XXiGxIzdpQAvf3otjUb'}, 'href': 'https://api.spotify.com/v1/artists/0B0XXiGxIzdpQAvf3otjUb', 'id': '0B0XXiGxIzdpQAvf3otjUb', 'name': 'ROUSSO', 'type': 'artist', 'uri': 'spotify:artist:0B0XXiGxIzdpQAvf3otjUb'}], 'album': {'album_name': 'VIEWS', 'album_group': None, 'album_type': 'single', 'released': '2020-02-24', 'spotify_id': '79ablxv5Re2WKtVnoSlTRt'}}, {'name': 'הטוב, הרע ואחותך', 'spotify_id': '6DtZXSfr5Ar5EWuTV9SPqV', 'duration_ms': 204350, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/17pbOSPIn3lmY0vHhOlKGL'}, 'href': 'https://api.spotify.com/v1/artists/17pbOSPIn3lmY0vHhOlKGL', 'id': '17pbOSPIn3lmY0vHhOlKGL', 'name': 'Tuna', 'type': 'artist', 'uri': 'spotify:artist:17pbOSPIn3lmY0vHhOlKGL'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/1Eks6sKVw6yepoeTbWv0YD'}, 'href': 'https://api.spotify.com/v1/artists/1Eks6sKVw6yepoeTbWv0YD', 'id': '1Eks6sKVw6yepoeTbWv0YD', 'name': 'Shalom Hanoch', 'type': 'artist', 'uri': 'spotify:artist:1Eks6sKVw6yepoeTbWv0YD'}], 'album': {'album_name': 'הטוב, הרע ואחותך', 'album_group': None, 'album_type': 'single', 'released': '2020-08-30', 'spotify_id': '2V8DasOxVYyo4iXqhhwC3S'}}, {'name': 'הייאוש תמיד שם', 'spotify_id': '2Qg0e4a8ue7FmSGWohrKIO', 'duration_ms': 115220, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/73tBbTv9s3yeK5cuTvl0vg'}, 'href': 'https://api.spotify.com/v1/artists/73tBbTv9s3yeK5cuTvl0vg', 'id': '73tBbTv9s3yeK5cuTvl0vg', 'name': 'Imri Cohen', 'type': 'artist', 'uri': 'spotify:artist:73tBbTv9s3yeK5cuTvl0vg'}], 'album': {'album_name': 'הייאוש תמיד שם (כשאתה זקוק לו)', 'album_group': None, 'album_type': 'album', 'released': '2020-07-03', 'spotify_id': '7sDWuEWwLQfmNaQGcvhuaE'}}, {'name': 'ים יבשה', 'spotify_id': '7al2sq1bYcP7m4dipzX8Vg', 'duration_ms': 189434, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/0QRKWNU8pxIapKWMqgX72s'}, 'href': 'https://api.spotify.com/v1/artists/0QRKWNU8pxIapKWMqgX72s', 'id': '0QRKWNU8pxIapKWMqgX72s', 'name': 'Omer Moskovich', 'type': 'artist', 'uri': 'spotify:artist:0QRKWNU8pxIapKWMqgX72s'}], 'album': {'album_name': 'ים יבשה', 'album_group': None, 'album_type': 'single', 'released': '2020-03-08', 'spotify_id': '5Q7nkRDR2KLWM4ZOL6TnQn'}}, {'name': 'גיטרה ופסנתר', 'spotify_id': '6XPAI7soLj5dPaTAOX4wrz', 'duration_ms': 228214, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/5OTBHykSuThA0RdYZTvDa2'}, 'href': 'https://api.spotify.com/v1/artists/5OTBHykSuThA0RdYZTvDa2', 'id': '5OTBHykSuThA0RdYZTvDa2', 'name': 'Aya Zahavi Feiglin', 'type': 'artist', 'uri': 'spotify:artist:5OTBHykSuThA0RdYZTvDa2'}], 'album': {'album_name': 'גיטרה ופסנתר', 'album_group': None, 'album_type': 'single', 'released': '2020-02-09', 'spotify_id': '3a7j14QGtGqWMcvTb5GT11'}}, {'name': 'חלום', 'spotify_id': '6BKWTDMtkPNsZ7TnexX3YJ', 'duration_ms': 217626, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/6pWlrO8XntD4d40ByhEr6B'}, 'href': 'https://api.spotify.com/v1/artists/6pWlrO8XntD4d40ByhEr6B', 'id': '6pWlrO8XntD4d40ByhEr6B', 'name': 'חומר אפל', 'type': 'artist', 'uri': 'spotify:artist:6pWlrO8XntD4d40ByhEr6B'}], 'album': {'album_name': 'חלום', 'album_group': None, 'album_type': 'single', 'released': '2020-10-16', 'spotify_id': '2911CLTIZ9gZnzmNH2Jdpo'}}, {'name': 'עצות', 'spotify_id': '5EhC2BUjGztiF0AQlqZEtG', 'duration_ms': 336614, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/0QRKWNU8pxIapKWMqgX72s'}, 'href': 'https://api.spotify.com/v1/artists/0QRKWNU8pxIapKWMqgX72s', 'id': '0QRKWNU8pxIapKWMqgX72s', 'name': 'Omer Moskovich', 'type': 'artist', 'uri': 'spotify:artist:0QRKWNU8pxIapKWMqgX72s'}], 'album': {'album_name': 'נצטרף לעדר', 'album_group': None, 'album_type': 'album', 'released': '2020-08-07', 'spotify_id': '2wBmHeVTVT2aopWpFurbsk'}}, {'name': 'כדור הארץ', 'spotify_id': '6jOIj1kZhS6nOoKaxhv515', 'duration_ms': 214169, 'artist': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/3fkSMBA8257Dyu7Hdlljob'}, 'href': 'https://api.spotify.com/v1/artists/3fkSMBA8257Dyu7Hdlljob', 'id': '3fkSMBA8257Dyu7Hdlljob', 'name': 'הנוקמים 2', 'type': 'artist', 'uri': 'spotify:artist:3fkSMBA8257Dyu7Hdlljob'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/24Rzfui4UwLMlhZcWYYk7P'}, 'href': 'https://api.spotify.com/v1/artists/24Rzfui4UwLMlhZcWYYk7P', 'id': '24Rzfui4UwLMlhZcWYYk7P', 'name': 'Hila Ruach', 'type': 'artist', 'uri': 'spotify:artist:24Rzfui4UwLMlhZcWYYk7P'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/1WbEiQdyarzwPjdOlUeOJU'}, 'href': 'https://api.spotify.com/v1/artists/1WbEiQdyarzwPjdOlUeOJU', 'id': '1WbEiQdyarzwPjdOlUeOJU', 'name': 'Ryskinder', 'type': 'artist', 'uri': 'spotify:artist:1WbEiQdyarzwPjdOlUeOJU'}], 'album': {'album_name': 'כדור הארץ', 'album_group': None, 'album_type': 'single', 'released': '2020-05-14', 'spotify_id': '55SgvFfOTgWIpfuBUr8ZV2'}}]}
    """
    collection, created = Collection.objects.get_or_create(
        name=d["name"],
        nick_name="",
        description=d["description"],
        created_year=int(d["created_date"][0:4]),
        ordinal=d["ordinal"]
    )
    if not created:
        collection.trackincollection_set.all().delete()

    def modify_track(t):
        #  so this is compatible with how the other method expects it
        return {
            "name": t["name"],
            "artist": ",".join([a["name"] for a in t["artist"]]),
            "duration": str(t["duration_ms"] / 1000),
            "released_year": int(t["album"]["released"][0:4]),
        }

    # Safe to key by name as it is unique
    artists = dict(
        [(a.name, a) for a in Artist.objects.all()]
    )
    tracks = [
        modify_track(t)
        for t in d["tracks"]
    ]

    tracks = [_get_or_create_track(t, artists)[1] for t in tracks]
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
