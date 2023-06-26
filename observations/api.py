import arrow
import datetime
from rest_framework import viewsets
from django.conf.urls import url
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework as filters

from penguins.utils import ListResourceView, DetailResourceView
from .models import PenguinUser, PenguinCount, PenguinObservation, Video


class PenguinCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PenguinCount.objects.all()


class PenguinObservationViewSet(viewsets.ModelViewSet):
    queryset = PenguinObservation.objects.all()


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('camera', 'date')

    def partial_update(self, request, pk=None):
        if 'mark_complete' in request.DATA:
            if request.DATA['mark_complete']:
                self.get_object().completed_by.add(request.user)

                pobs = PenguinObservation.objects.filter(
                    video=self.get_object(),
                    observer=request.user)  # .update(validated=True)
                for obs in pobs:
                    obs.validated = True
                    obs.save()
                if pobs.count() == 0:
                    d = self.get_object().date
                    hour = self.get_object().end_time.hour
                    observation_date = datetime.datetime(
                        d.year,
                        d.month,
                        d.day,
                        hour,
                        0)
                    p = PenguinObservation(
                        video=self.get_object(),
                        observer=request.user,
                        seen=0,
                        comments="[default]No penguins reported",
                        validated=True,
                        date=observation_date)
                    p.save()
            else:
                self.get_object().completed_by.remove(request.user)
        response = super(VideoViewSet, self).partial_update(request, pk)
        return response


def penguinsobservation_serializer(obj):
    return {
        'id': obj.pk,
        'date': obj.video.date.isoformat(),
        'video_id': obj.video.pk,
        'observer_id': obj.observer.pk,
        'seen': obj.seen,
        'position': obj.position,
        'comments': obj.comments,
        'validated': obj.validated,
    }


class PenguinObservationSerializer(object):

    def serialize(obj):
        return penguinsobservation_serializer(obj)


@method_decorator(csrf_exempt, name='dispatch')
class PenguinObservationListResource(LoginRequiredMixin, ListResourceView):
    model = PenguinObservation
    serializer = PenguinObservationSerializer
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            new_obs = PenguinObservation(
                date=arrow.get(data['date']).datetime,
                video=Video.objects.get(pk=data['video']),
                observer=PenguinUser.objects.get(pk=data['observer']),
                seen=data['seen'],
                position=data['position'],
                comments=data['comments'] if data['comments'] else None,
                validated=data['validated'] == 'true',
            )
            new_obs.save()
            return JsonResponse(penguinsobservation_serializer(new_obs))
        except:
            return HttpResponseBadRequest('Invalid request data')


@method_decorator(csrf_exempt, name='dispatch')
class PenguinObservationDetailResource(LoginRequiredMixin, DetailResourceView):
    model = PenguinObservation
    serializer = PenguinObservationSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'trace']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(request.POST)
        return HttpResponse('Tried to update {}'.format(self.object))


def video_serializer(obj):
    return {
        'id': obj.pk,
        'name': obj.name,
        'date': obj.date.isoformat(),
        'camera_id': obj.camera.pk,
        'file': obj.file.name,
        'start_time': obj.start_time.isoformat(),
        'end_time': obj.end_time.isoformat(),
        'views': obj.views,
        'mark_complete': obj.mark_complete,
    }


class VideoSerializer(object):

    def serialize(obj):
        return video_serializer(obj)


class VideoListResource(LoginRequiredMixin, ListResourceView):
    model = Video
    serializer = VideoSerializer


@method_decorator(csrf_exempt, name='dispatch')
class VideoDetailResource(LoginRequiredMixin, DetailResourceView):
    model = Video
    serializer = VideoSerializer

    # TODO: patch/post method


V2_API_URLS = [
    url(r'^observation/$', PenguinObservationListResource.as_view(), name='penguinobservation_list_resource'),
    url(r'^observation/(?P<pk>\d+)/$', PenguinObservationDetailResource.as_view(), name='penguinobservation_detail_resource'),
    url(r'^video/$', VideoListResource.as_view(), name='video_list_resource'),
    url(r'^video/(?P<pk>\d+)/$', VideoDetailResource.as_view(), name='video_detail_resource'),
]
