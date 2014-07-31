from django.conf import settings
from django.conf.urls import patterns, include, url

from rest_framework.routers import DefaultRouter

from observations.sites import site
from observations.api import PenguinCountViewSet, PenguinObservationViewSet


router = DefaultRouter()
router.register(r'count', PenguinCountViewSet)
router.register(r'observations', PenguinObservationViewSet)

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^help/', include('django.contrib.flatpages.urls')),
    url(r'', include(site.urls)),
)
