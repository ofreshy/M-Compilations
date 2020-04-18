from collections import defaultdict


from django.db import models

from musik_lib.models.base import Artist, Collection, Library, Track


class LibraryStat(models.Model):
    library = models.OneToOneField(
        Library,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def add_artist_frequency_counts(self):
        """

        :return:
        """
        frequency_counts = defaultdict(int)
        unique_artists = dict()
        cafcs = [
            cafc for c_stat in self.collectionstat_set.all()
            for cafc in c_stat.artistfrequencycollection_set.all()
        ]
        for cafc in cafcs:
            frequency_counts[cafc.artist.id] += cafc.frequency
            unique_artists[cafc.artist.id] = cafc.artist

        for artist_id, frequency in frequency_counts.items():
            artist = unique_artists[artist_id]
            afl = ArtistFrequencyLibrary.objects.get_or_create(
                artist=artist,
                library_stat=self
            )[0]
            afl.frequency = frequency
            afl.save()
            self.artistfrequencylibrary_set.add(afl)


class DuplicateTrack(models.Model):
    track = models.OneToOneField(
        Track,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class CollectionStat(models.Model):
    """
    The stat extension of the collection model.

    """
    collection = models.OneToOneField(
        Collection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    library_stat = models.ForeignKey(
        LibraryStat,
        on_delete=models.CASCADE,
        default=None,
    )
    duplicate_tracks = models.ManyToManyField(DuplicateTrack)

    def add_artist_frequency_counts(self):
        """

        :return: updated artist frequency counts of this collection stat
        """
        frequency_counts = defaultdict(int)
        unique_artists = dict()

        artists = [a for track in self.collection.track_set.all() for a in track.artist_set.all()]
        for artist in artists:
            frequency_counts[artist.id] += 1
            unique_artists[artist.id] = artist

        for artist_id, frequency in frequency_counts.items():
            artist = unique_artists[artist_id]
            afc = ArtistFrequencyCollection.objects.get_or_create(
                artist=artist,
                collection_stat=self
            )[0]
            afc.frequency = frequency
            afc.save()
            self.artistfrequencycollection_set.add(afc)


class ArtistFrequencyCollection(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
    )
    collection_stat = models.ForeignKey(
        CollectionStat,
        on_delete=models.CASCADE
    )
    frequency = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['artist', 'collection_stat'], name='Artist And Collection')
        ]

    def __str__(self):
        return "{} - {} - {}".format(self.artist.name, self.collection_stat.collection.name, self.frequency)


class ArtistFrequencyLibrary(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
    )
    library_stat = models.ForeignKey(
        LibraryStat,
        on_delete=models.CASCADE
    )
    frequency = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return "{} - {}".format(self.artist.name, self.frequency)
