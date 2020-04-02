
# Create your views here.
from django.http import HttpResponse


def index(_):
    return HttpResponse("Hello, world.")
