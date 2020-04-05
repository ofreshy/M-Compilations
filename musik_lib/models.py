import operator
from functools import reduce


from django.db import models
from django.utils import timezone


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

    created_year = models.PositiveSmallIntegerField()
    ordinal = models.PositiveSmallIntegerField(unique=True)

    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    def __str__(self):
        return "name={} , nick_name = {}, ordinal = {}".format(self.name, self.nick_name, self.ordinal)

    def duration(self):
        return reduce(operator.add, [t.duration for t in self.track_set.all()])


class Track(models.Model):
    """
        Music track
    """

    @classmethod
    def create_track(cls, name):
        return Track(name=name, released_date=timezone.now())

    name = models.CharField(max_length=1000)
    duration = models.DurationField()
    released_year = models.PositiveSmallIntegerField()

    collection = models.ManyToManyField(Collection)

    def __str__(self):
        return self.name


class Artist(models.Model):
    """
        An artist with a name and can be a band
    """
    name = models.CharField(max_length=200)

    track = models.ManyToManyField(Track)

    def __str__(self):
        return self.name
