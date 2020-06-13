
from django.test import TestCase

from musik_lib.models.base import *
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
        self.assertEqual(c.duration.seconds, 0)

    def test_duration_sum(self):
        c = fixtures.collection_1()

        duration1 = datetime.timedelta(minutes=0, seconds=18)
        duration2 = datetime.timedelta(minutes=0, seconds=100)
        t1 = fixtures.track_1(duration=duration1)
        t2 = fixtures.track_2(duration=duration2)

        c.add_tracks([t1, t2])

        actual = c.duration
        expected = t1.duration + t2.duration

        self.assertEqual(actual.seconds, expected.seconds)

    def test_order_of_tracks_in_collection(self):
        pass



    def test_empty_tracks(self):
        c = fixtures.collection_1()
        self.assertEqual(c.number_of_tracks(), 0)

    def test_track_count(self):
        c = fixtures.collection_1()

        c = c.add_tracks([fixtures.track_1(), fixtures.track_2()])

        self.assertEqual(c.number_of_tracks(), 2)


    def test_track_add_ordinal(self):
        c = fixtures.collection_1()
        t2, t1 = fixtures.track_2(), fixtures.track_1()

        c = c.add_tracks([t1, t2])

        self.assertEqual([t for t in c.tracks], [t1, t2])

    def test_track_add_respects_order_when_called_twice(self):
        c = fixtures.collection_1()
        t1, t2, t3 = fixtures.track_1(), fixtures.track_2(), fixtures.track_3()

        c = c.add_tracks([t1, t2])
        c = c.add_tracks([t3])

        self.assertEqual([t for t in c.tracks], [t1, t2, t3])



class TrackTest(TestCase):
    def test_artist_names_single(self):
        t = fixtures.track_1(name="t1")
        t.artist.add(
            fixtures.artist_1(name="a1")
        )
        self.assertEqual(t.artist_names, "a1")

    def test_artist_names_several(self):
        t = fixtures.track_1(name="t1")
        t.artist.add(
            fixtures.artist_1(name="a1"),
            fixtures.artist_1(name="a2")
        )
        self.assertEqual(t.artist_names, "a1 & a2")

    def test_artist_names_feat(self):
        t = fixtures.track_1(name="t1")
        t.artist.add(
            fixtures.artist_1(name="a1"),
        )
        t.featuring.add(
            fixtures.artist_1(name="a2"),
        )
        self.assertEqual(t.artist_names, "a1 Feat. a2")

    def test_collection_property_when_empty(self):
        self.assertFalse(fixtures.track_1().collections)


    def test_collection_property_when_added_to_collections(self):
        t = fixtures.track_1()

        c1 = fixtures.collection_1().add_tracks([t])
        c2 = fixtures.collection_2().add_tracks([t])

        self.assertEqual(t.collections, [c1, c2])


class TrackInCollectionTest(TestCase):

    def test_collection_track_constraint(self):
        c = fixtures.collection_1(name="c1")
        TrackInCollection.objects.create(
            track=fixtures.track_1(name="t1"),
            collection=c,
            ordinal=1,
        )
        # Test the constraint for ordinal in the collection
        with self.assertRaises(Exception):
            TrackInCollection.objects.create(
                track=fixtures.track_1(name="t2"),
                collection=c,
                ordinal=1,
            )
