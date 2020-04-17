
from musik_lib.models.base import *

from collections import defaultdict


def calculate_artist_frequency_collection(c_stat: CollectionStat):

    frequency_counts = defaultdict(int)
    unique_artists = dict()

    artists = [a for track in c_stat.collection.track_set.all() for a in track.artist_set.all()]
    for artist in artists:
        frequency_counts[artist.id] += 1
        unique_artists[artist.id] = artist

    for artist_id, frequency in frequency_counts.items():
        yield ArtistFrequencyCollection(
                artist=unique_artists[artist_id],
                collection_stat=c_stat,
                frequency=frequency,
            )
