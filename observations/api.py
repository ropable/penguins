from rest_framework import viewsets
from rest_framework import filters

from observations.models import PenguinCount, PenguinObservation, Video
from utils import RetrievePartialUpdateDestroyAPIView;


class PenguinCountViewSet(viewsets.ReadOnlyModelViewSet):
    model = PenguinCount


class PenguinObservationViewSet(viewsets.ModelViewSet):
    model = PenguinObservation


class VideoViewSet(viewsets.ModelViewSet):
    model = Video
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('camera', 'date')

    def partial_update(self, request, pk=None):
        if request.DATA.has_key('mark_complete'):
            if request.DATA['mark_complete']:
                self.get_object().completed_by.add(request.user)

                pobs= PenguinObservation.objects.filter(video=self.get_object(),
                                                     observer=request.user)#.update(validated=True)
                for obs in pobs:
                    obs.validated = True
                    obs.save()
            else:
                self.get_object().completed_by.remove(request.user)
        response =super(VideoViewSet,self).partial_update(request,pk)
        return response

