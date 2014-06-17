from rest_framework import viewsets
from rest_framework import filters

from observations.models import PenguinCount, PenguinObservation, Video


class PenguinCountViewSet(viewsets.ReadOnlyModelViewSet):
    model = PenguinCount


class PenguinObservationViewSet(viewsets.ModelViewSet):
    model = PenguinObservation


class VideoViewSet(viewsets.ModelViewSet):
    model = Video
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('camera', 'date')
