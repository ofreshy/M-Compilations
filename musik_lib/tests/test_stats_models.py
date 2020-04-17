from django.test import TestCase

from musik_lib.tests import fixtures


class CollectionStatTest(TestCase):

    def test_empty_collections_stat_empty_stats(self):
        c_stat = fixtures.collection_stat_1()
        c_stat.add_artist_frequency_counts()
        artist_frequency_counts = c_stat.artistfrequencycollection_set.all()
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

        c_stat = fixtures.collection_stat_1(collection=c1)

        c_stat.add_artist_frequency_counts()

        result = c_stat.artistfrequencycollection_set.all()

        self.assertEqual(len(result), 1)
        artist_frequency_count = result[0]
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

        c_stat = fixtures.collection_stat_1(collection=c1)

        c_stat.add_artist_frequency_counts()
        result = c_stat.artistfrequencycollection_set.all()

        self.assertEqual(len(result), 2)
        a1_result = next(x for x in result if x.artist.id == a1.id)
        a2_result = next(x for x in result if x.artist.id == a2.id)
        self.assertIsNotNone(a1_result)
        self.assertIsNotNone(a2_result)

        self.assertEqual(a1_result.frequency, 2)
        self.assertEqual(a2_result.frequency, 1)




