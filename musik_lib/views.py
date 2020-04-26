

from django.shortcuts import get_object_or_404, render
from django.views import generic

from musik_lib.models.stats import *


class IndexView(generic.ListView):
    template_name = 'musik_lib/lib.html'
    context_object_name = 'collections'

    def get_queryset(self):
        """Return the last five published questions."""
        return Collection.objects.order_by('ordinal')


class CollectionDetailView(generic.DetailView):
    model = Collection
    template_name = 'musik_lib/collection.html'


class TrackDetailView(generic.DetailView):
    model = Track
    template_name = 'musik_lib/track.html'


class TrackListView(generic.ListView):
    template_name = 'musik_lib/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        """Return the last five published questions."""
        return Track.objects.order_by('name')


def artist(request, artist_id):
    _artist = get_object_or_404(Artist, pk=artist_id)
    tracks = _artist.track.all()
    collections = []
    for t in tracks:
        collections.extend((c.id, c) for c in t.collection.all())
    unique_collections = list(dict(collections).values())
    sorted_collections = sorted(unique_collections, key=lambda x: x.ordinal)

    context = {
        "artist": _artist,
        "tracks": tracks,
        "collections": sorted_collections
    }
    return render(request, 'musik_lib/artist.html', context)


def lib_stat(request):
    context = {
        "lib_stat": LibraryStat.load(),
    }
    return render(request, 'musik_lib/lib_stat.html', context)


class ArtistListView(generic.ListView):
    template_name = 'musik_lib/artist_list.html'
    context_object_name = 'artists'

    def get_queryset(self):
        """Return the last five published questions."""
        return Artist.objects.order_by('name')


class CollectionStatListView(generic.ListView):
    template_name = 'musik_lib/collections_stat_list.html'
    context_object_name = 'collections_stats'

    def get_queryset(self):
        """Return the last five published questions."""
        return CollectionStat.objects.order_by('collection_id')


class CollectionStatDetailView(generic.DetailView):
    model = CollectionStat
    template_name = 'musik_lib/collection_stat.html'
    context_object_name = 'c_stat'


class DuplicateTrackDetailView(generic.DetailView):
    model = DuplicateTrack
    template_name = 'musik_lib/duplicate_track.html'
    context_object_name = 'dt'


class DuplicateTrackListView(generic.ListView):
    template_name = 'musik_lib/dt_list.html'
    context_object_name = 'dts'

    def get_queryset(self):
        """Return the last five published questions."""
        return DuplicateTrack.objects.all()


class ArtistFrequencyCollectionDetailView(generic.DetailView):
    model = ArtistFrequencyCollection
    template_name = 'musik_lib/afc.html'
    context_object_name = 'afc'


class ArtistFrequencyLibraryDetailView(generic.DetailView):
    model = ArtistFrequencyLibrary
    template_name = 'musik_lib/afl.html'
    context_object_name = 'afl'


class ArtistFrequencyLibraryListView(generic.ListView):
    template_name = 'musik_lib/afl_list.html'
    context_object_name = 'afls'

    def get_queryset(self):
        """Return the last five published questions."""
        return ArtistFrequencyLibrary.objects.order_by('-frequency')
