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


class Artist(models.Model):
    """
        An artist
    """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    @property
    def tracks(self):
        tracks = []
        if hasattr(self, "main_artist"):
            tracks.extend([t for t in self.main_artist.all()])
        if hasattr(self, "featured_artist"):
            tracks.extend([t for t in self.featured_artist.all()])
        return tracks


class Track(models.Model):
    """
        Music track
    """

    name = models.CharField(max_length=1000)
    duration = models.DurationField()
    released_year = models.PositiveSmallIntegerField(validators=[validate_year])

    artist = models.ManyToManyField(Artist, related_name='main_artist')
    featuring = models.ManyToManyField(Artist, related_name='featured_artist')

    def __str__(self):
        return "{} - {}".format(self.name, self.artist_names)

    @property
    def artist_names(self):
        artist_names = ""
        artists = self.artist.all()
        if artists:
            artist_names += " & ".join([a.name for a in artists])
        featuring = self.featuring.all()
        if featuring:
            artist_names += " Feat. "
            artist_names += " & ".join([a.name for a in featuring])
        return artist_names

    @property
    def artists(self):
        return [a for a in self.artist.all()] + [a for a in self.featuring.all()]


class Collection(models.Model):
    """
    Collection stores some tracks
    """

    name = models.CharField(max_length=200)
    nick_name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=2000)

    created_year = models.PositiveSmallIntegerField(validators=[validate_year])
    ordinal = models.PositiveSmallIntegerField(unique=True)

    track = models.ManyToManyField(Track)

    def __str__(self):
        return "name={} , nick_name = {}, duration = {}".format(self.name, self.nick_name, self.duration)

    @property
    def duration(self):
        return total_durations(
            [t.duration for t in self.track.all()]
        )

    def number_of_tracks(self):
        if hasattr(self, "track"):
            return self.track.count()
        else:
            return 0


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
            [t.duration for t in Collection.objects.all()]
        )

    @property
    def collections(self):
        return Collection.objects.all()
