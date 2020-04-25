from django.urls import path
from musik_lib import views

app_name = 'lib'
urlpatterns = [
    # ex: /lib/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /collection/1/
    path('collection/<int:pk>/', views.CollectionView.as_view(), name='collection'),
    # ex: /track/5/
    path('track/<int:pk>/', views.TrackView.as_view(), name='track'),
    # ex: /artist/5/
    path('artist/<int:artist_id>/', views.artist, name='artist'),

    # ex: /collection_stat/
    path('collection_stat/', views.CollectionStatsView.as_view(), name='collections_stats'),
    # ex: /collection_stat/5/
    path('collection_stat/<int:pk>/', views.collection_stats_view, name='collection_stats'),

    # ex: /afc/5/
    path('afc/<int:pk>/', views.afc, name='afc'),
]
