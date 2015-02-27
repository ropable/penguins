from rest_framework import viewsets
from rest_framework import filters

from observations.models import PenguinCount, PenguinObservation, Video
from utils import RetrievePartialUpdateDestroyAPIView;
import datetime


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
                if pobs.count() == 0:
                    d=self.get_object().date
                    hour=self.get_object().end_time.hour
                    observation_date=datetime.datetime(d.year, d.month, d.day, hour, 0)
                    p = PenguinObservation( video=self.get_object(),
                                            observer=request.user,
                                            site = self.get_object().camera.site,
                                            seen=0,
                                            comments="[default]No penguins reported",
                                            validated=True,
                                            date=observation_date
                                           )
                    p.save()
            else:
                self.get_object().completed_by.remove(request.user)
        response =super(VideoViewSet,self).partial_update(request,pk)
        return response

