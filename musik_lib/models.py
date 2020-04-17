import datetime
import operator

from functools import reduce

from django.db import models

from musik_lib.validators import validate_year


class Library(models.Model):
    """
    The library holds all collections and it is a singleton class
    """

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Library, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Collection(models.Model):
    """
    Collection stores some tracks
    """

    name = models.CharField(max_length=200)
    nick_name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=2000)

    created_year = models.PositiveSmallIntegerField(validators=[validate_year])
    ordinal = models.PositiveSmallIntegerField(unique=True)

    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    def __str__(self):
        return "name={} , nick_name = {}, ordinal = {}".format(self.name, self.nick_name, self.ordinal)

    def duration(self):
        return reduce(
            operator.add,
            [t.duration for t in self.track_set.all()],
            datetime.timedelta()
        )

    def number_of_tracks(self):
        return len(self.track_set.all())


class Track(models.Model):
    """
        Music track
    """

    name = models.CharField(max_length=1000)
    duration = models.DurationField()
    released_year = models.PositiveSmallIntegerField(validators=[validate_year])

    collection = models.ManyToManyField(Collection)

    def __str__(self):
        return self.name


class Artist(models.Model):
    """
        An artist
    """
    name = models.CharField(max_length=200, unique=True)

    track = models.ManyToManyField(Track)

    def __str__(self):
        return self.name


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
