#from daterange_filter.filter import DateRangeFilter
from django.urls import path, reverse
from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import unquote, quote
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from functools import update_wrapper

from .models import Video


class DetailChangeList(ChangeList):
    def url_for_result(self, result):
        if self.model_admin.changelist_link_detail:
            pk = getattr(result, self.pk_attname)
            return reverse('admin:%s_%s_detail' % (self.opts.app_label,
                                                   self.opts.module_name),
                           args=(quote(pk),),
                           )
        else:
            return super(DetailChangeList, self).url_for_result(result)


class DetailAdmin(ModelAdmin):
    detail_template = None
    changelist_link_detail = False
    change_form_template = None

    def get_changelist(self, request, **kwargs):
        return DetailChangeList

    def has_view_permission(self, request, obj=None):
        return True

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            path('/', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            path('add/', wrap(self.add_view), name='%s_%s_add' % info),
            #path('(\d+)/history/', wrap(self.history_view), name='%s_%s_history' % info),
            #path('(\d+)/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
            #path('(\d+)/change/', wrap(self.change_view), name='%s_%s_change' % info),
            #path('(\d+)/', wrap(self.detail_view), name='%s_%s_detail' % info),
        ]
        return urlpatterns

    def detail_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        opts = self.opts
        if not self.has_view_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404('{} object with primary key {} does not exist.'.format(force_str(opts.verbose_name), escape(object_id)))

        context = {
            'title': 'Detail {}'.format(force_str(opts.verbose_name)),
            'object_id': object_id,
            'original': obj,
            'media': self.media,
            'app_label': opts.app_label,
            'opts': opts,
            'has_change_permission': self.has_change_permission(request, obj),
        }
        context.update(extra_context or {})
        return TemplateResponse(
            request,
            self.detail_template or [
                "admin/%s/%s/detail.html" % (opts.app_label, opts.object_name.lower()),
                "admin/%s/detail.html" % opts.app_label,
                "admin/detail.html"
            ],
            context,
        )

    def queryset(self, request):
        qs = super(DetailAdmin, self).queryset(request)
        return qs.select_related(
            *[field.rsplit('__', 1)[0]
              for field in self.list_display if '__' in field]
        )


class CameraAdmin(DetailAdmin):
    actions = None
    list_display = ("name", "camera_key", "active", "video_count", "newest_video")
    fields = ("name", "camera_key", "active", "location")

    def video_count(self, obj):
        count = Video.objects.filter(camera_id=obj.pk).count()
        return str(count)

    def newest_video(self, obj):
        video = obj.get_newest_video()
        if video:
            return video.get_start_datetime()
        else:
            return ""

    def detail_view(self, request, object_id, extra_context=None):
        opts = self.opts
        obj = self.get_object(request, unquote(object_id))

        if not self.has_view_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404('{} object with primary key {} does not exist.'.format(force_str(opts.verbose_name), escape(object_id)))

        # Return a paginated list of videos.
        video_qs = obj.video_set.all()
        paginator = Paginator(video_qs, 50)
        page = request.GET.get('page')
        try:
            videos = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            videos = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            videos = paginator.page(paginator.num_pages)

        context = {
            'title': '{} camera'.format(obj.name),
            'videos': videos,
            'video_count': video_qs.count(),
            'can_add_observations': request.user.is_observer() or request.user.is_superuser,
        }
        context.update(extra_context or {})
        return super(CameraAdmin, self).detail_view(request, object_id, context)


class PenguinObservationAdmin(ModelAdmin):
    actions = ["delete", "export_to_csv"]
    date_hierarchy = 'date'
    list_display = (
        "video_date",
        "video_start_time",
        "link_to_video",
        "position",
        "seen",
        "observer",
        "validated",
    )
    #list_filter = (("video__date", DateRangeFilter), "validated")
    fields = ("video_date", "video_start_time", "video", "position", "seen", "comments", "observer", "validated")
    readonly_fields = ("video", "video_date", "video_start_time")

    def video_date(self, obj):
        return obj.video.date
    video_date.short_description = "date"

    def video_start_time(self, obj):
        return obj.video.start_time
    video_start_time.short_description = "start time"

    def link_to_video(self, obj):
        return mark_safe("<a href='{}'>{}</a>".format(reverse("admin:observations_video_detail", args=(obj.video.pk,)), obj.video))
    link_to_video.short_description = "Video"

    def save_model(self, request, obj, form, change):
        obj.observer = request.user
        obj.save()

    def response_post_save_add(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when adding a new object.
        """
        opts = self.model._meta
        site_id = request.GET.get('site', None)
        if site_id is not None:
            post_url = reverse('admin:observations_site_detail', args=(site_id,))
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url)
            return HttpResponseRedirect(post_url)
        else:
            return super(PenguinObservationAdmin, self).response_post_save_add(request, obj)


class VideoAdmin(DetailAdmin):
    date_hierarchy = 'date'
    list_display = ('camera', 'file', 'date', 'start_time', 'end_time')
    fields = ('date', 'camera', 'file', 'start_time', 'end_time', 'views', 'mark_complete', 'completed_by')
    readonly_fields = ('date', 'camera', 'file', 'start_time', 'end_time', 'views')
    filter_horizontal = ('completed_by',)

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def detail_view(self, request, object_id, extra_context=None):
        opts = self.opts
        obj = self.get_object(request, unquote(object_id))
        obj.views += 1
        obj.save()

        # If the user is neither a superuser nor part of the Observer group, disallow usage.
        #if not request.user.is_superuser and not request.user.is_observer():
        #    raise PermissionDenied

        if obj is None:
            raise Http404('{} object with primary key {} does not exist.'.format(force_str(opts.verbose_name), escape(object_id)))

        observations = obj.penguinobservation_set.filter(observer=request.user).order_by("position")

        context = {
            'title': 'View video',
            'user_observations': observations,
        }
        context.update(extra_context or {})
        return super(VideoAdmin, self).detail_view(request, object_id, context)
