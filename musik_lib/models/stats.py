from collections import defaultdict


from musik_lib.models.base import *


class LibraryStat(models.Model):
    library = models.OneToOneField(
        Library,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1, library=Library.load())
        return obj

    @property
    def num_collections(self):
        return Collection.objects.count()

    @property
    def num_tracks(self):
        return Track.objects.count()

    @property
    def num_artists(self):
        return Artist.objects.count()

    @property
    def duration(self):
        return self.library.duration

    def update(self):
        self.update_collection_stats()
        self.update_artist_frequency_counts()
        self.update_duplicate_tracks()

    def update_collection_stats(self):
        for coll in self.library.collections:
            c_stat, _ = CollectionStat.objects.get_or_create(collection=coll)
            c_stat.update()

    def update_artist_frequency_counts(self):
        """

        :return:
        """

        frequency_counts = defaultdict(int)
        unique_artists = dict()

        def add_collection_counts(cafcs):
            for cafc in cafcs:
                frequency_counts[cafc.artist.id] += cafc.frequency
                unique_artists[cafc.artist.id] = cafc.artist

        def add_artist_frequency_library(artist, frequency):
            afl, _ = ArtistFrequencyLibrary.objects.get_or_create(
                artist=artist,
                library_stat=self,
            )
            afl.frequency = frequency
            afl.save()
            self.artistfrequencylibrary_set.add(afl)

        for c_stat in self.collection_stats:
            add_collection_counts(c_stat.update_artist_frequency_counts())

        for aid, freq in frequency_counts.items():
            add_artist_frequency_library(unique_artists[aid], freq)
        
        return self.artistfrequencylibrary_set.all()

    @property
    def collection_stats(self):
        return CollectionStat.objects.all()

    def update_duplicate_tracks(self):
        track_counts = [
            (track, c_stat, track.trackincollection_set.count()) for c_stat in self.collection_stats
            for track in c_stat.collection.tracks
        ]
        duplicate_tracks = [tup for tup in track_counts if tup[2] > 1]

        for track, c_stat, frequency in duplicate_tracks:
            dt = DuplicateTrack.objects.get_or_create(track=track)[0]
            dt.frequency = frequency
            dt.save()
            c_stat.duplicate_tracks.add(dt)
            c_stat.save()
        return DuplicateTrack.objects.all()


class DuplicateTrack(models.Model):
    track = models.OneToOneField(
        Track,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    frequency = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return "{} - {}".format(self.track, self.frequency)

    @property
    def name(self):
        return self.track.name


class CollectionStat(models.Model):
    """
    The stat extension of the collection model.

    """
    collection = models.OneToOneField(
        Collection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    duplicate_tracks = models.ManyToManyField(DuplicateTrack)

    def __str__(self):
        return "Stats for {} ".format(self.collection.name)

    def update(self):
        self.update_artist_frequency_counts()

    def update_artist_frequency_counts(self):
        """

        :return: updated artist frequency counts of this collection stat
        """
        frequency_counts = defaultdict(int)
        unique_artists = dict()

        artists = [a for track in self.collection.tracks for a in track.artists]
        for artist in artists:
            frequency_counts[artist.id] += 1
            unique_artists[artist.id] = artist

        for artist_id, frequency in frequency_counts.items():
            artist = unique_artists[artist_id]
            afc = ArtistFrequencyCollection.objects.get_or_create(
                artist=artist,
                collection_stat=self,
            )[0]
            afc.frequency = frequency
            afc.save()
            self.artistfrequencycollection_set.add(afc)
        return self.artistfrequencycollection_set.all()


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
        return "{} - {}".format(self.artist.name, self.frequency)

    @property
    def tracks(self):
        return [t for t in self.collection_stat.collection.tracks if t.artist == self.artist]


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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['artist', 'library_stat'], name='Artist And Library')
        ]

    def __str__(self):
        return "{} - {}".format(self.artist.name, self.frequency)

    @property
    def tracks(self):
        return self.artist.tracks
