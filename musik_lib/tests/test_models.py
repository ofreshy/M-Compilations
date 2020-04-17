
from django.test import TestCase

from musik_lib.models import *
from musik_lib.tests import fixtures


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
        c = fixtures.collection_1()
        self.assertEqual(c.duration().seconds, 0)

    def test_duration_sum(self):
        c = fixtures.collection_1()

        duration1 = datetime.timedelta(minutes=0, seconds=18)
        duration2 = datetime.timedelta(minutes=0, seconds=100)
        t1 = fixtures.track_1(duration=duration1)
        t2 = fixtures.track_2(duration=duration2)

        c.track_set.add(t1, t2)

        actual = c.duration()
        expected = t1.duration + t2.duration

        self.assertEqual(actual.seconds, expected.seconds)

    def test_empty_track_set(self):
        c = fixtures.collection_1()
        self.assertEqual(c.number_of_tracks(), 0)

    def test_track_set_count(self):
        c = fixtures.collection_1()

        t1 = fixtures.track_1()
        t2 = fixtures.track_2()

        c.track_set.add(t1, t2)

        self.assertEqual(c.number_of_tracks(), 2)
