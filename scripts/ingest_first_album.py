import django
django.setup()


from django.utils.dateparse import parse_duration

from musik_lib.models import *

data = [
    "Any Day Now,Elbow,6:18",
    "fear of fireflies, Calla, 4:17",
    "wish fulfilment, sonic youth, 3:27",
    "Plug in Baby, Muse, 3:39",
    "Stereo, Pavement, 3:10",
    "Miner at the dial view, Granddady, 5:22",
    "So You'll aim to the sky, Granddady, 4:44",
    "Novocain for the Soul, Eals, 3:09",
    "Today, Smashing Pumpkins, 3:23",
    "Monkey's Gone to Heaven, Pixies, 2:59",
    "Cannonball, Breeders, 3:34",
    "The Mess We're in, PJ Harvey & Thom Yorke, 3:56",
    "Night as Rain, Deus, 4:28",
    "Angelene, PJ Harvey, 3:35",
]


def cleanup_db():
    Library.objects.all().delete()
    Collection.objects.all().delete()
    Track.objects.all().delete()
    Artist.objects.all().delete()


def ingest_data(d):
    l = Library(id=1)
    l.save()

    collection = Collection(
        name="My First Album",
        nick_name="My First",
        description="My ever first album",
        created_year=2001,
        ordinal=1,
        library=l,
        id=1,
    )
    collection.save()

    artists = dict()
    for line in d:
        track_name, artists_name, duration = [s.strip() for s in line.split(",")]

        track = Track(
            name=track_name,
            duration=parse_duration(duration),
            released_year=2001,
        )
        track.save()

        artists_list = [a.strip() for a in artists_name.split("&")]
        for artist_name in artists_list:
            if artist_name not in artists.keys():
                artist = Artist(name=artist_name)
                artist.save()
                artists[artist_name] = artist
            track.artist_set.add(artists[artist_name])
        track.save()

        collection.track_set.add(track)

    collection.save()


def main():
    print("Start")
    cleanup_db()
    ingest_data(data)
    print("Finish")


if __name__ == '__main__':
    main()


