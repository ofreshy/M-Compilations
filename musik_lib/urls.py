from django.urls import path
from musik_lib import views

app_name = 'lib'
urlpatterns = [
    # ex: /lib/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /collection/1/
    path('collection/<int:pk>/', views.CollectionDetailView.as_view(), name='collection'),

    # ex: /track/
    path('track/', views.TrackListView.as_view(), name='track'),
    # ex: /track/5/
    path('track/<int:pk>/', views.TrackDetailView.as_view(), name='track'),

    # ex: /artist
    path('artist/', views.ArtistListView.as_view(), name='artists'),
    # ex: /artist/5/
    path('artist/<int:artist_id>/', views.artist, name='artist'),

    # ex: /lib_stat/
    path('lib_stat/', views.lib_stat, name='lib_stat'),

    # ex: /collection_stat/
    path('collection_stat/', views.CollectionStatListView.as_view(), name='collections_stats'),
    # ex: /collection_stat/5/
    path('collection_stat/<int:pk>/', views.CollectionStatDetailView.as_view(), name='collection_stats'),

    # ex: /afc
    path('afc/', views.ArtistFrequencyCollectionListView.as_view(), name='afcs'),
    # ex: /afc/5/
    path('afc/<int:pk>/', views.ArtistFrequencyCollectionDetailView.as_view(), name='afc'),

    # ex: /dt
    path('dt/', views.DuplicateTrackListView.as_view(), name='dts'),
    # ex: /dt/5/
    path('dt/<int:pk>/', views.DuplicateTrackDetailView.as_view(), name='dt'),

    # ex: /afl/
    path('afl/', views.ArtistFrequencyLibraryListView.as_view(), name='afls'),
    # ex: /afl/5/
    path('afl/<int:pk>/', views.ArtistFrequencyLibraryDetailView.as_view(), name='afl'),
]
