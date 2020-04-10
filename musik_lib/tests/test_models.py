
from django.test import TestCase

from musik_lib.models import *


def create_collection():
    return Collection(
        name="C1",
        nick_name="to2",
        description="test",
        created_year=2000,
        ordinal=1,
        library=Library.load()
    )


class LibraryTest(TestCase):

    def test_singleton(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        l1 = Library()
        l2 = Library()
        l1.save()
        l2.save()
        self.assertEqual(l1.id, 1)
        self.assertEqual(l1.id, l2.id)


class CollectionTest(TestCase):

    def test_empty_collection_duration(self):
        c = create_collection()
        c.save()
        self.assertEqual(c.duration().seconds, 0)

    def test_duration_sum(self):
        c = create_collection()
        c.save()

        t1 = Track(name="t1", released_year=1979, duration=datetime.timedelta(minutes=0, seconds=18))
        t2 = Track(name="t2", released_year=2001, duration=datetime.timedelta(minutes=0, seconds=100))
        t1.save()
        t2.save()

        c.track_set.add(t1)
        c.track_set.add(t2)

        actual = c.duration()
        expected = t1.duration + t2.duration

        self.assertEqual(actual.seconds, expected.seconds)

    def test_empty_track_set(self):
        c = create_collection()
        c.save()
        self.assertEqual(c.number_of_tracks(), 0)

    def test_track_set_count(self):
        c = create_collection()
        c.save()

        t1 = Track(name="t1", released_year=1979, duration=datetime.timedelta(minutes=0, seconds=18))
        t2 = Track(name="t2", released_year=2001, duration=datetime.timedelta(minutes=0, seconds=100))
        t1.save()
        t2.save()

        c.track_set.add(t1)
        c.track_set.add(t2)

        self.assertEqual(c.number_of_tracks(), 2)

