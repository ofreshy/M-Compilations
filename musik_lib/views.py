
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from musik_lib.models import Artist, Collection, Library, Track


def index(request):
    root_lib = Library.objects.get(id=1)
    context = {'collections': root_lib.collection_set.all()}
    return render(request, 'musik_lib/lib.html', context)


def collection(request, collection_id):
    context = {"collection": get_object_or_404(Collection, pk=collection_id)}
    return render(request, 'musik_lib/collection.html', context)


def track(request, track_id):
    context = {"track": get_object_or_404(Track, pk=track_id)}
    return render(request, 'musik_lib/track.html', context)


def artist(request, artist_id):
    context = {"artist": get_object_or_404(Artist, pk=artist_id)}
    return render(request, 'musik_lib/artist.html', context)
