from django.db import models

class DuplicateTrack(models.Model):
    track = models.OneToOneField(
        Track,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class LibraryStat(models.Model):
    library = models.OneToOneField(
        Library,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class CollectionStat(models.Model):
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
