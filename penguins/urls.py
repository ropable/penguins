from __future__ import absolute_import
from django.conf.urls import include, url
from observations.api import API_URLS
from observations.sites import site
from observations.views import HelpPage

urlpatterns = [
    url(r'^api/', include((API_URLS, 'observations'), namespace='api')),
    url(r'^help/', HelpPage.as_view(), name='help_page'),
    url(r'', include(site.urls)),
]
