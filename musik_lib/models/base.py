import datetime
import operator

from itertools import chain
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


def render_duration(duration):
    """
    Helper function to render duration
    0:ss for less than a minute songs
    m:ss for less than 10 minutes
    mm:ss for less than an hour
    h:mm:ss for more than an hour
    :param duration: a duration object (time delta)
    :return:
    """
    total_seconds = int(duration.total_seconds())
    seconds = (total_seconds % 3600) % 60
    minutes = (total_seconds % 3600) // 60
    hours = total_seconds // 3600

    if hours >= 24:
        days = hours // 24
        hours = hours % 24
        return "{} days and {}:{:02}:{:02} hours".format(days, hours, minutes, seconds)
    if hours:
        return "{}:{:02}:{:02} hours".format(hours, minutes, seconds)
    if minutes:
        return "{}:{:02} minutes".format(minutes, seconds)
    else:
        return "0:{:02} seconds".format(total_seconds)


class Artist(models.Model):
    """
        An artist
    """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    @property
    def tracks(self):
        return [
            t for t
            in chain(
                self.main_artist.all(),
                self.featured_artist.all(),
            )
        ]


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
        template = "{} - {} - {}"
        values = self.name, self.artist_names, render_duration(self.duration)
        return template.format(*values)

    @property
    def artist_names(self):
        artist_names = ""

        artists = self.artist.all()
        if artists:
            artist_names += " , ".join([a.name for a in artists])

        featuring = self.featuring.all()
        if featuring:
            artist_names += " Feat. " + " , ".join([a.name for a in featuring])

        return artist_names

    @property
    def artists(self):
        return [a for a in self.artist.all()] + [a for a in self.featuring.all()]

    @property
    def collections(self):
        tracks_in_collection = self.trackincollection_set.all() if hasattr(self, "trackincollection_set") else []
        return [t.collection for t in tracks_in_collection]


class Collection(models.Model):
    """
    Collection stores some tracks
    """

    name = models.CharField(max_length=200)
    nick_name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=2000)

    created_year = models.PositiveSmallIntegerField(validators=[validate_year])
    ordinal = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        template = "name={} , nick_name = {}, duration = {}"
        values = self.name, self.nick_name, render_duration(self.duration)
        return template.format(*values)

    @property
    def duration(self):
        return total_durations(
            [t.duration for t in self.tracks]
        )

    def number_of_tracks(self):
        return self.trackincollection_set.count() if hasattr(self, "trackincollection_set") else 0

    @property
    def tracks(self):
        return [t.track for t in self.trackincollection_set.order_by('ordinal')]

    def add_tracks(self, tracks):
        """

        :param tracks: Track objects. Assume that the order of this list maps to their order in the collection
        :return:
        """
        start_index = self.number_of_tracks() + 1
        for ind, track in enumerate(tracks):
            TrackInCollection.objects.create(track=track, collection=self, ordinal=start_index + ind)
        return self


class TrackInCollection(models.Model):
    """
    A track in a collection; Separate from a track as it has a unique ordinal in the collection
    """
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    ordinal = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['collection', 'ordinal'], name='Collection and Ordinal')
        ]

    def __str__(self):
        return "track={} , ordinal = {}".format(self.track, self.ordinal)


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
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def duration(self):
        return total_durations(
            [t.duration for t in self.collections]
        )

    @property
    def collections(self):
        return Collection.objects.all()
