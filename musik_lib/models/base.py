import datetime
import operator

from functools import reduce

from django.db import models

from musik_lib.validators import validate_year


def total_durations(durations):
    """
    Helper function to add durations
    :param durations:
    :return:
    """
    return reduce(operator.add, durations, datetime.timedelta())


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

    @property
    def duration(self):
        return total_durations(
            [t.duration for t in self.collection_set.all()]
        )


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
        return "name={} , nick_name = {}, duration = {}".format(self.name, self.nick_name, self.duration)

    @property
    def duration(self):
        return total_durations(
            [t.duration for t in self.track_set.all()]
        )

    def number_of_tracks(self):
        if hasattr(self, "track_set"):
            return len(self.track_set.all())
        else:
            return 0


class Track(models.Model):
    """
        Music track
    """

    name = models.CharField(max_length=1000)
    duration = models.DurationField()
    released_year = models.PositiveSmallIntegerField(validators=[validate_year])

    collection = models.ManyToManyField(Collection)

    def __str__(self):
        disp = self.name
        if hasattr(self, "artist_set"):
            artists = " & ".join([a.name for a in self.artist_set.all()])
            disp += " - {}".format(artists)
        disp += " - " + str(self.duration)
        return disp


class Artist(models.Model):
    """
        An artist
    """
    name = models.CharField(max_length=200, unique=True)

    track = models.ManyToManyField(Track)

    def __str__(self):
        return self.name
