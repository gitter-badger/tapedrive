from django.conf import settings
from django.urls import include, path
from . import views
from . import api

app_name = 'podcasts'

episodes_patterns = [
    path('<uuid:id>/', include([
        # path('position/<int:position>', views.podcasts_refresh_feed, name='podcasts-refresh-feed'),
        path('played/', api.episodes_mark_played, name='episodes-mark-played'),
        # path('unplayed/', views.episodes_mark_unplayed, name='episodes-mark-unplayed'),
    ]))
]

podcasts_api_patterns = [
    path('refresh-feed/', api.podcast_refresh_feed, name='api-refresh-feed'),
    path('subscribe/', api.podcast_subscribe, name='api-subscribe'),
    path('unsubscribe/', api.podcast_unsubscribe, name='api-unsubscribe'),
    # path('episodes/', include(episodes_patterns)),
]


podcasts_patterns = [
    path('', views.podcasts_list, name='podcasts-list'),
    path('discover/', views.podcasts_discover, name='podcasts-discover'),
    path('new/', views.podcasts_new, name='podcasts-new'),
    path('<slug:slug>/', include([
        path('', views.podcasts_details, name='podcasts-details'),
        path('api/', include(podcasts_api_patterns)),
        path('refresh/', views.podcasts_refresh_feed, name='podcasts-refresh-feed'),
    ]))
]

urlpatterns = [
    path('', views.index, name='index'),
    path('podcasts/', include(podcasts_patterns)),
    path('settings/', views.settings, name='settings'),
]
