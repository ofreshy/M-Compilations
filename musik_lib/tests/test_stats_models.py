from django.test import TestCase

from musik_lib.tests import fixtures


class CollectionStatTest(TestCase):

    def test_empty_collections_stat_empty_stats(self):
        c_stat = fixtures.collection_stat()
        artist_frequency_counts = c_stat.update_artist_frequency_counts()
        self.assertFalse(artist_frequency_counts)

    def test_artist_collections_stat_single_artist(self):
        artist = fixtures.artist_1()

        t1 = fixtures.track_1()
        t2 = fixtures.track_2()

        t1.artist_set.add(artist)
        t2.artist_set.add(artist)

        t1.save()
        t2.save()

        c1 = fixtures.collection_1()
        c1.track_set.add(t1, t2)
        c1.save()

        c_stat = fixtures.collection_stat(collection=c1)

        artist_frequency_counts = c_stat.update_artist_frequency_counts()

        self.assertEqual(len(artist_frequency_counts), 1)
        artist_frequency_count = artist_frequency_counts[0]
        self.assertEqual(artist_frequency_count.artist, artist)
        self.assertEqual(artist_frequency_count.frequency, 2)

    def test_artist_collections_stat_several_artist(self):
        a1 = fixtures.artist_1()
        a2 = fixtures.artist_2()

        t1 = fixtures.track_1()
        t2 = fixtures.track_2()

        t1.artist_set.add(a1)
        t2.artist_set.add(a1, a2)

        t1.save()
        t2.save()

        c1 = fixtures.collection_1()
        c1.track_set.add(t1, t2)
        c1.save()

        c_stat = fixtures.collection_stat(collection=c1)

        artist_frequency_counts = c_stat.update_artist_frequency_counts()

        self.assertEqual(len(artist_frequency_counts), 2)
        a1_result = next(x for x in artist_frequency_counts if x.artist.id == a1.id)
        a2_result = next(x for x in artist_frequency_counts if x.artist.id == a2.id)
        self.assertIsNotNone(a1_result)
        self.assertIsNotNone(a2_result)

        self.assertEqual(a1_result.frequency, 2)
        self.assertEqual(a2_result.frequency, 1)


class LibraryStatTest(TestCase):

    def test_add_artist_frequency_counts_when_empty(self):
        l_stat = fixtures.library_stat()
        artist_frequency_counts = l_stat.update_artist_frequency_counts()
        self.assertFalse(artist_frequency_counts)

    def test_add_artist_frequency_counts_when_two_collections(self):
        a1 = fixtures.artist_1()
        a2 = fixtures.artist_2()
        a3 = fixtures.artist_3()

        t1 = fixtures.track_1()
        t2 = fixtures.track_2()
        t3 = fixtures.track_3()

        c1 = fixtures.collection_1()
        c2 = fixtures.collection_2()

        # Wire the collections
        t1.artist_set.add(a1)
        t2.artist_set.add(a1, a2)
        t3.artist_set.add(a1, a2, a3)
        c1.track_set.add(t1, t2)  # a1 + a1+a2
        c2.track_set.add(t2, t3)  # a1+a2 + a1+a2+a3

        l_stat = fixtures.library_stat()
        _ = fixtures.collection_stat(collection=c1, lib_stat=l_stat)
        _ = fixtures.collection_stat(collection=c2, lib_stat=l_stat)

        artist_frequency_counts = l_stat.update_artist_frequency_counts()
        self.assertEqual(3, len(artist_frequency_counts))

        #  TODO move this to a Mixin
        a1_result = next(x for x in artist_frequency_counts if x.artist.id == a1.id)
        self.assertEqual(4, a1_result.frequency)

        a2_result = next(x for x in artist_frequency_counts if x.artist.id == a2.id)
        self.assertEqual(3, a2_result.frequency)

        a3_result = next(x for x in artist_frequency_counts if x.artist.id == a3.id)
        self.assertEqual(1, a3_result.frequency)
