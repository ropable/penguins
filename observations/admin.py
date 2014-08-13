from __future__ import unicode_literals

from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from swingers.admin import DetailAdmin
from leaflet.admin import LeafletGeoAdmin
from flatpages_x.admin import FlatPageAdmin
from django.utils.safestring import mark_safe
import datetime
import logging
import os
import subprocess
import unicodecsv
from observations.models import Video
from observations.forms import SelectDateForm

from daterange_filter.filter import DateRangeFilter

logger = logging.getLogger(__name__)


class BaseAdmin(ModelAdmin):

    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        context = {
            'title': self.get_title(request)
        }
        context.update(extra_context or {})
        return super(BaseAdmin, self).changelist_view(request, context)


class SiteAdmin(DetailAdmin, LeafletGeoAdmin):
    actions = None
    list_display = ('name', 'location')

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

        observations = obj.penguinobservation_set.filter(site=obj)[:10]

        # Define a set of videos to pass into the view on load.
        # All cameras, today's date.
        cams = obj.camera_set.all()
        initial_videos = Video.objects.filter(camera__in=cams, date=datetime.date.today())
        context = {
            'title': obj.name,
            'select_date': SelectDateForm,
            'initial_videos': initial_videos,
            'recent_observations': observations
        }
        context.update(extra_context or {})
        return super(SiteAdmin, self).detail_view(request, object_id, context)


class CameraAdmin(DetailAdmin):
    actions = None
    list_display = ('name', 'site', 'ip_address')

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

        observations = obj.penguinobservation_set.filter(site=obj)[:10]

        context = {
            'title': obj.name,
            'recent_observations': observations
        }
        context.update(extra_context or {})
        return super(SiteAdmin, self).detail_view(request, object_id, context)


class PenguinCountAdmin(ModelAdmin):
    actions = ['export_to_csv']
    list_display = ('date', 'sitelink', 'civil_twilight', 'sub_fifteen',
                    'zero_to_fifteen', 'fifteen_to_thirty',
                    'thirty_to_fourty_five', 'fourty_five_to_sixty',
                    'sixty_to_seventy_five', 'seventy_five_to_ninety',
                    'ninety_to_one_oh_five', 'one_oh_five_to_one_twenty',
                    'total_penguins', 'outlier', 'comments')

    list_per_page = 15
    def sitelink (self,item):
        return mark_safe('<a href="/observations/site/{0}/">{1}</a>'.format(item.site.pk,item.site.name))


    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = "attachment; filename=export.csv"

        writer = unicodecsv.writer(response, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow(['date', 'Civil Twilight Time', '-15 - 0', '1 - 15',
                         '16 - 30', '31-45', '46 - 60', '61 - 75', '76 - 90',
                         '91 - 105', '106 - 120', 'Total', 'outlier', 'Comments'])

        for item in queryset:
            writer.writerow([item.date, item.civil_twilight,
                item.sub_fifteen, item.zero_to_fifteen, item.fifteen_to_thirty, item.thirty_to_fourty_five,
                item.fourty_five_to_sixty, item.sixty_to_seventy_five, item.seventy_five_to_ninety,
                item.ninety_to_one_oh_five, item.one_oh_five_to_one_twenty, item.total_penguins,
                item.outlier, item.comments])

        return response
    export_to_csv.short_description = ugettext_lazy("Export to CSV")


class PenguinObservationAdmin(BaseAdmin):
    actions = ['delete','export_to_csv']
    list_display = ('date', 'site', 'camera', 'observer', 'seen', 'comments','link_to_video','position')
    list_filter = (('date', DateRangeFilter),'site', 'camera',)
    #readonly_fields = ('site',)
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('date', 'site', 'camera', 'seen', 'comments')
        }),
        (ugettext_lazy("Environmental conditions (optional)"), {
            'fields': (('wind_direction', 'wind_speed'),
                       ('wave_direction', 'wave_height', 'wave_period'),
                       'moon_phase')
        })
    )
    exclude = ('observer',)

    def link_to_video(self,obj):
        if (obj.video):
            #return mark_safe("<a href='/observations/video/"+str(obj.video.pk)+"'>"+str(obj.video)+"</a>")
            return mark_safe("<a href='"+reverse("admin:observations_video_detail",args=(obj.video.pk,))+"'>"+str(obj.video)+"</a>")
        else:
            return "No video"

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'camera':
            kwargs['empty_label'] = ugettext_lazy("None (In-situ)")
        return super(PenguinObservationAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.observer = request.user
        obj.save()

    def get_title(self, request):
        return ugettext_lazy("Penguin observations")

    def response_post_save_add(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when adding a new object.
        """
        opts = self.model._meta
        site_id = request.GET.get('site', None)
        if site_id is not None:
            post_url = reverse('admin:observations_site_detail',
                args=(site_id,), current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
            return HttpResponseRedirect(post_url)
        else:
            return super(PenguinObservationAdmin, self).response_post_save_add(request, obj)


class VideoAdmin(DetailAdmin):
    list_display = ('camera', 'name', 'start_time', 'end_time')
    exclude = ('views',)

    fieldsets = (
        (None, {
            'fields': ('camera', 'file', 'date', 'start_time', 'end_time'),
        }),
    )

    list_per_page = 15

    def detail_view(self, request, object_id, extra_context=None):
        opts = self.opts
        
        obj = self.get_object(request, unquote(object_id))

        obj.views += 1
        obj.save()

        if not self.has_view_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id)})


        observations = obj.camera.penguinobservation_set.filter(
            observer=request.user,
            date__range=(datetime.datetime.combine(obj.date, obj.start_time),
                         datetime.datetime.combine(obj.date, obj.end_time)))


        context = {
            'title': "View video",
            'user_observations': observations
        }
        context.update(extra_context or {})
        return super(VideoAdmin, self).detail_view(request, object_id, context)

class HelpCMS(FlatPageAdmin):
    fieldsets=((None, {'fields': ('url', 'title', 'content_md', 'sites')}),)
    list_display = ('url', 'title')
    list_filter = ('sites',)
    search_fields = ('url', 'title')

