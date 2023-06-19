from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter

from observations.sites import site
from observations.api import PenguinCountViewSet, PenguinObservationViewSet, VideoViewSet
from observations.views import HelpPage


router = DefaultRouter()
router.register(r'count', PenguinCountViewSet)
router.register(r'observations', PenguinObservationViewSet)
router.register(r'videos', VideoViewSet)

urlpatterns = patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^help/', HelpPage.as_view(), name='help_page'),
    url(r'', include(site.urls)),
)
