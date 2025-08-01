import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.detail import SingleObjectMixin

from penguins.utils import breadcrumbs_html, get_next_pages, get_previous_pages, user_can_add_observations

from .models import Camera, PenguinObservation, Video


class SiteHome(LoginRequiredMixin, TemplateView):
    """Static template view for the site homepage."""

    template_name = "observations/site_home.html"
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["page_title"] = "Penguins | Home"
        context["page_heading"] = "Penguin Island cameras"
        context["geoserver_url"] = settings.GEOSERVER_URL
        context["layer_name"] = settings.LAYER_NAME
        queryset = Camera.objects.filter(active=True)
        context["active_cameras"] = queryset
        # Pass a list of cameras to the template context
        cameras_list = [
            {
                "pk": camera.pk,
                "name": camera.name,
                "x": camera.location.x,
                "y": camera.location.y,
            }
            for camera in queryset
        ]
        context["cameras_json"] = json.dumps(cameras_list)
        links = [(None, "Home")]
        context["breadcrumb_trail"] = breadcrumbs_html(links)
        return context


class HelpPage(LoginRequiredMixin, TemplateView):
    """Help page (static template view)."""

    template_name = "observations/help_page.html"
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Penguins | Help page"
        links = [(reverse("observations:site_home"), "Home"), (None, "Help")]
        context["breadcrumb_trail"] = breadcrumbs_html(links)
        if settings.EXAMPLE_VIDEO_URL:
            context["example_video_url"] = settings.EXAMPLE_VIDEO_URL
        else:
            context["example_video_url"] = None
        return context


class VideoList(LoginRequiredMixin, ListView):
    """User-facing list view for all videos."""

    template_name = "observations/video_list.html"
    model = Video
    paginate_by = 50
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("camera_id"):
            queryset = queryset.filter(camera__pk=self.request.GET["camera_id"])
        if self.request.GET.get("date"):
            # Django is nice enough to parse the date string for us.
            queryset = queryset.filter(date=self.request.GET["date"])
        if self.request.GET.get("completed"):
            completed = self.request.GET["completed"] == "true"
            queryset = queryset.filter(mark_complete=completed)
        if self.request.GET.get("views"):
            if self.request.GET["views"] == "false":
                queryset = queryset.filter(views=0)
            elif self.request.GET["views"] == "true":
                queryset = queryset.filter(views__gt=0)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["can_add_observations"] = user_can_add_observations(self.request.user)
        context["page_title"] = "Penguins | Videos"
        context["page_heading"] = "Penguin Island videos"
        context["object_count"] = len(self.get_queryset())
        context["previous_pages"] = get_previous_pages(context["page_obj"])
        context["next_pages"] = get_next_pages(context["page_obj"])
        context["active_cameras"] = Camera.objects.filter(active=True)
        links = [(reverse("observations:site_home"), "Home"), (None, "Videos")]
        context["breadcrumb_trail"] = breadcrumbs_html(links)
        # Context for filter form.
        if self.request.GET.get("camera_id"):
            context["filter_camera_id"] = int(self.request.GET["camera_id"])
        if self.request.GET.get("date"):
            context["filter_date"] = self.request.GET["date"]
        if self.request.GET.get("completed"):
            context["filter_completed"] = self.request.GET["completed"]
        if self.request.GET.get("views"):
            context["filter_views"] = self.request.GET["views"]
        return context


class VideoDetail(LoginRequiredMixin, DetailView):
    """User-facing detail view for a single video, used to record new observations."""

    template_name = "observations/video_detail.html"
    model = Video
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["superuser"] = True
        context["can_add_observations"] = user_can_add_observations(self.request.user)
        obj = self.get_object()
        context["page_title"] = f"Penguins | {obj}"
        links = [
            (reverse("observations:site_home"), "Home"),
            (reverse("observations:video_list"), "Videos"),
            (None, obj.pk),
        ]
        context["breadcrumb_trail"] = breadcrumbs_html(links)
        return context


class VideoObservations(LoginRequiredMixin, ListView):
    """Basic view to return the penguin observation objects for a given video, for the request user."""

    template_name = "observations/video_observations_table.html"
    model = PenguinObservation
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        video = Video.objects.get(pk=self.kwargs["pk"])
        qs = qs.filter(video=video, observer=self.request.user).order_by("position")
        return qs


class PenguinObservationCreate(LoginRequiredMixin, SingleObjectMixin, View):
    """API endpoint to create a new PenguinObservation on a parent Video."""

    model = Video
    http_method_names = ["post", "head", "options"]

    def dispatch(self, request, *args, **kwargs):
        if not user_can_add_observations(request.user):
            return HttpResponseForbidden("Unauthorised")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        video = self.get_object()
        observation = PenguinObservation.objects.create(
            video=video,
            observer=request.user,
            position=int(request.POST["videoPosition"]),
            count=request.POST["penguinCount"],
            comments=request.POST["comments"],
        )
        d = {
            "id": observation.pk,
            "video_id": observation.video.pk,
            "observer": observation.observer.get_full_name(),
            "position": observation.position,
            "count": observation.count,
            "comments": observation.comments,
            "timestamp": observation.get_observation_datetime().isoformat(),
        }
        return JsonResponse(d)


class VideoComplete(LoginRequiredMixin, SingleObjectMixin, View):
    """API endpoint to mark a Video as 'complete'."""

    model = Video
    http_method_names = ["patch", "head", "options"]

    def dispatch(self, request, *args, **kwargs):
        if not user_can_add_observations(request.user):
            return HttpResponseForbidden("Unauthorised")
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        video = self.get_object()
        video.mark_complete = True
        video.views = video.views + 1
        video.completed_by.add(request.user)
        video.save()
        d = {
            "id": video.pk,
            "date": video.date,
            "camera": str(video.camera),
            "file": video.file.url,
            "start_time": video.start_time,
            "end_time": video.end_time,
            "views": video.views,
            "mark_complete": video.mark_complete,
        }
        return JsonResponse(d)
