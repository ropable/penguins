from __future__ import unicode_literals
from datetime import datetime, date
from daterange_filter.filter import DateRangeFilter
from django.conf import settings
from django.conf.urls import url
from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import unquote, quote
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from functools import update_wrapper
from leaflet.admin import LeafletGeoAdmin
import unicodecsv

from .models import Video
from .forms import SelectDateForm


class DetailChangeList(ChangeList):
    def url_for_result(self, result):
        if self.model_admin.changelist_link_detail:
            pk = getattr(result, self.pk_attname)
            return reverse('admin:%s_%s_detail' % (self.opts.app_label,
                                                   self.opts.module_name),
                           args=(quote(pk),),
                           #current_app=self.model_admin.admin_site.name
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
        opts = self.opts
        return request.user.has_perm(
            opts.app_label + '.' + 'view_%s' % opts.object_name.lower()
        )

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^$',
                wrap(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%s_%s_add' % info),
            url(r'^(\d+)/history/$',
                wrap(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(\d+)/delete/$',
                wrap(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(\d+)/change/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
            url(r'^(\d+)/$',
                wrap(self.detail_view),
                name='%s_%s_detail' % info),
        ]
        return urlpatterns

    def detail_view(self, request, object_id, extra_context=None):
        opts = self.opts

        obj = self.get_object(request, unquote(object_id))

        if not self.has_view_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        context = {
            'title': _('Detail %s') % force_text(opts.verbose_name),
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
            #current_app=self.admin_site.name
        )

    def queryset(self, request):
        qs = super(DetailAdmin, self).queryset(request)
        return qs.select_related(
            *[field.rsplit('__', 1)[0]
              for field in self.list_display if '__' in field]
        )


class SiteAdmin(DetailAdmin, LeafletGeoAdmin):
    actions = None
    list_display = ('name', 'location')

    def has_view_permission(self, request, obj=None):
        return True

    def detail_view(self, request, object_id, extra_context=None):
        opts = self.opts
        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id)})

        observations = obj.penguinobservation_set.filter(site=obj)[:10]

        # Define a set of videos to pass into the view on load.
        # All cameras, today's date.
        cams = obj.camera_set.all()
        initial_videos = Video.objects.filter(
            camera__in=cams,
            date=date.today())
        context = {
            'title': obj.name,
            'select_date': SelectDateForm,
            'initial_videos': initial_videos,
            'recent_observations': observations,
            'can_add_observations': request.user.is_observer() or request.user.is_superuser,
        }
        context.update(extra_context or {})
        return super(SiteAdmin, self).detail_view(request, object_id, context)


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
            raise Http404('%(name)s object with primary key %(key)r does not exist.' % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id)
            })

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


class PenguinCountAdmin(ModelAdmin):
    actions = ['export_to_csv']
    list_display = ('date', 'sitelink', 'civil_twilight', 'sub_fifteen',
                    'zero_to_fifteen', 'fifteen_to_thirty',
                    'thirty_to_fourty_five', 'fourty_five_to_sixty',
                    'sixty_to_seventy_five', 'seventy_five_to_ninety',
                    'ninety_to_one_oh_five', 'one_oh_five_to_one_twenty',
                    'total_penguins', 'outlier', 'comments')

    def sitelink(self, obj):
        return mark_safe(
            '<a href="/observations/site/{0}/">{1}</a>'.format(obj.site.pk, obj.site.name))

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=penguin_count_{}_{}.csv'.format(date.today().isoformat(), datetime.now().strftime('%H%M'))

        writer = unicodecsv.writer(response, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow(['date',
                         'Site link',
                         'Civil Twilight Time',
                         '-15 - 0',
                         '1 - 15',
                         '16 - 30',
                         '31-45',
                         '46 - 60',
                         '61 - 75',
                         '76 - 90',
                         '91 - 105',
                         '106 - 120',
                         'Total',
                         'outlier',
                         'Comments'])

        for obj in queryset:
            writer.writerow([
                obj.date,
                '{}{}'.format(
                    settings.SITE_URL,
                    reverse(
                        'admin:observations_site_detail',
                        args=(obj.site.pk,),
                        #current_app=self.admin_site.name
                    ),
                ),
                obj.civil_twilight,
                obj.sub_fifteen,
                obj.zero_to_fifteen,
                obj.fifteen_to_thirty,
                obj.thirty_to_fourty_five,
                obj.fourty_five_to_sixty,
                obj.sixty_to_seventy_five,
                obj.seventy_five_to_ninety,
                obj.ninety_to_one_oh_five,
                obj.one_oh_five_to_one_twenty,
                obj.total_penguins,
                obj.outlier,
                obj.comments])

        return response
    export_to_csv.short_description = ugettext_lazy("Export to CSV")


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
    list_filter = (("video__date", DateRangeFilter), "validated")
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

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=penguin_observations_{}_{}.csv'.format(date.today().isoformat(), datetime.now().strftime('%H%M'))
        writer = unicodecsv.writer(response, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow([
            "date",
            "camera",
            "video",
            "observer",
            "seen at (AWST)",
            "count",
            "validated",
            "comments",
        ])

        for obj in queryset:
            writer.writerow([
                obj.video.date.strftime("%d/%b/%Y"),
                obj.video.camera,
                obj.video,
                obj.observer.get_full_name(),
                obj.get_observation_datetime().strftime("%d/%b/%Y %H:%M:%S"),
                obj.seen,
                obj.validated,
                obj.comments,
            ])
        return response
    export_to_csv.short_description = ugettext_lazy("Export to CSV")

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
        if not request.user.is_superuser and not request.user.is_observer():
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id)})

        observations = obj.penguinobservation_set.filter(observer=request.user)

        context = {
            'title': 'View video',
            'user_observations': observations,
        }
        context.update(extra_context or {})
        return super(VideoAdmin, self).detail_view(request, object_id, context)
