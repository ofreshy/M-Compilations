from django.db import models
from django.utils import timezone


class Library(models.Model):
    pass


class Collection(models.Model):
    """
    Collection stores some tracks
    """

    name = models.CharField(max_length=200)
    nick_name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=2000)
    # TODO constraint here for past data only
    created_date = models.DateTimeField()
    ordinal = models.PositiveSmallIntegerField()

    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    def __str__(self):
        return "name={} , nick_name = {}, ordinal = {}".format(self.name, self.nick_name, self.ordinal)


class Track(models.Model):
    """
        Music track
    """

    @classmethod
    def create_track(cls, name):
        return Track(name=name, released_date=timezone.now())

    name = models.CharField(max_length=1000)
    length = models.TimeField(null=True)
    released_date = models.DateTimeField()

    collection = models.ManyToManyField(Collection)

    def __str__(self):
        return self.name


class Artist(models.Model):
    """
        An artist with a name and can be a band
    """
    name = models.CharField(max_length=200)
    is_band = models.BooleanField()

    track = models.ManyToManyField(Track)

    def __str__(self):
        return self.name + (" (BAND)" if self.is_band else "")
