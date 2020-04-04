from django.urls import path
from musik_lib import views


urlpatterns = [
    # ex: /lib/
    path('', views.index, name='index'),
    # ex: /collection/1/
    path('collection/<int:collection_id>/', views.collection, name='collection'),
    # ex: /track/5/
    path('track/<int:track_id>/', views.track, name='track'),
    # ex: /artist/5/
    path('artist/<int:artist_id>/', views.artist, name='artist'),
]
