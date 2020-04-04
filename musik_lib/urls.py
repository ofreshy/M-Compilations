from django.urls import path
from musik_lib import views


urlpatterns = [
    # ex: /lib/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('collection/<int:collection_id>/', views.collection, name='collection'),
    # ex: /polls/5/results/
    path('track/<int:track_id>/', views.track, name='track'),
    # ex: /polls/5/vote/
    path('artist/<int:artist_id>/', views.artist, name='artist'),
]
