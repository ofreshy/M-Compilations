
from django.db.models.functions import Upper
from django.shortcuts import render
from django.views import generic

from musik_lib.models.stats import *


class IndexView(generic.ListView):
    template_name = 'musik_lib/lib.html'
    context_object_name = 'collections'

    def get_queryset(self):
        return Collection.objects.order_by('ordinal')


def lib_stat(request):
    context = {
        "lib_stat": LibraryStat.load(),
    }
    return render(request, 'musik_lib/lib_stat.html', context)


class CollectionDetailView(generic.DetailView):
    model = Collection
    template_name = 'musik_lib/collection.html'


class CollectionListView(generic.ListView):
    template_name = 'musik_lib/collection_list.html'
    context_object_name = 'collections'

    def get_queryset(self):
        """Return the last five published questions."""
        return Collection.objects.order_by('ordinal')


class TrackDetailView(generic.DetailView):
    model = Track
    template_name = 'musik_lib/track.html'


class TrackListView(generic.ListView):
    template_name = 'musik_lib/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        """Return the last five published questions."""
        return Track.objects.order_by('name')


class ArtistDetailView(generic.DetailView):
    model = Artist
    template_name = 'musik_lib/artist.html'


class ArtistListView(generic.ListView):
    template_name = 'musik_lib/artist_list.html'
    context_object_name = 'artists'
    paginate_by = 100

    def get_queryset(self):
        return Artist.objects.order_by(Upper('name'))


class CollectionStatListView(generic.ListView):
    template_name = 'musik_lib/collections_stat_list.html'
    context_object_name = 'collections_stats'

    def get_queryset(self):
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


class ArtistFrequencyCollectionListView(generic.ListView):
    template_name = 'musik_lib/afc_list.html'
    context_object_name = 'afcs'

    def get_queryset(self):
        return ArtistFrequencyCollection.objects.order_by('-frequency', Upper("artist__name"))


class ArtistFrequencyLibraryDetailView(generic.DetailView):
    model = ArtistFrequencyLibrary
    template_name = 'musik_lib/afl.html'
    context_object_name = 'afl'


class ArtistFrequencyLibraryListView(generic.ListView):
    template_name = 'musik_lib/afl_list.html'
    context_object_name = 'afls'

    def get_queryset(self):
        return ArtistFrequencyLibrary.objects.order_by('-frequency', Upper("artist__name"))
