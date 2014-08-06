from rest_framework import viewsets

from observations.models import PenguinCount, PenguinObservation, Video
from utils import RetrievePartialUpdateDestroyAPIView;


class PenguinCountViewSet(viewsets.ReadOnlyModelViewSet):
    model = PenguinCount

class PenguinObservationViewSet(viewsets.ModelViewSet):
    model = PenguinObservation

class VideoViewSet(viewsets.ModelViewSet):
    model = Video


    def partial_update(self, request, pk=None):
        if request.DATA.has_key('mark_complete'):
            if request.DATA['mark_complete']:
                self.get_object().completed_by.add(request.user)
            else:
                self.get_object().completed_by.remove(request.user)
        response =super(VideoViewSet,self).partial_update(request,pk)
        return response

