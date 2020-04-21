

from django.shortcuts import get_object_or_404, render
from django.views import generic

from musik_lib.models.base import Artist, Collection, Library, Track


class IndexView(generic.ListView):
    template_name = 'musik_lib/lib.html'
    context_object_name = 'collections'

    def get_queryset(self):
        """Return the last five published questions."""
        return Collection.objects.order_by('ordinal')


class CollectionView(generic.DetailView):
    model = Collection
    template_name = 'musik_lib/collection.html'


class TrackView(generic.DetailView):
    model = Collection
    template_name = 'musik_lib/track.html'


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
