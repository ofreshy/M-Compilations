
# Create your views here.
from django.http import HttpResponse

from musik_lib.models import *


def index(_):
    l = Library.objects.get(id=1)
    collections = l.collection_set.all()
    names = ",".join([c.name for c in collections])
    return HttpResponse("Library contains the following collections %s" % names)


def collection(request, collection_id):
    return HttpResponse("You're looking at collection %s." % collection_id)


def track(request, track_id):
    return HttpResponse("You're looking at track %s." % track_id)


def artist(request, artist_id):
    return HttpResponse("You're looking at artist %s." % artist_id)
