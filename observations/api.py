import arrow
from django.conf.urls import url
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from penguins.utils import ListResourceView, DetailUpdateResourceView
from .models import PenguinUser, PenguinObservation, Video


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
class PenguinObservationDetailResource(LoginRequiredMixin, DetailUpdateResourceView):
    model = PenguinObservation
    serializer = PenguinObservationSerializer

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
    http_method_names = ['get', 'head', 'options', 'trace']


@method_decorator(csrf_exempt, name='dispatch')
class VideoDetailResource(LoginRequiredMixin, DetailUpdateResourceView):
    model = Video
    serializer = VideoSerializer

    def post(self, request, *args, **kwargs):
        data = request.POST
        video = self.get_object()
        # "Mark as complete" function.
        if "mark_complete" in data and data["mark_complete"]:
            video.mark_complete = True
            video.completed_by.add(request.user)
            video.save()
            return HttpResponse("OK")

        return


API_URLS = [
    url(r'^observation/$', PenguinObservationListResource.as_view(), name='penguinobservation_list_resource'),
    url(r'^observation/(?P<pk>\d+)/$', PenguinObservationDetailResource.as_view(), name='penguinobservation_detail_resource'),
    url(r'^video/$', VideoListResource.as_view(), name='video_list_resource'),
    url(r'^video/(?P<pk>\d+)/$', VideoDetailResource.as_view(), name='video_detail_resource'),
]
