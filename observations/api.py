from rest_framework import viewsets

from observations.models import PenguinCount, PenguinObservation


class PenguinCountViewSet(viewsets.ReadOnlyModelViewSet):
    model = PenguinCount

class PenguinObservationViewSet(viewsets.ModelViewSet):
    model = PenguinObservation
