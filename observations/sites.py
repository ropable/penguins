from arrow import Arrow
from collections import OrderedDict
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Count
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .admin import (SiteAdmin, CameraAdmin, PenguinCountAdmin,
                    PenguinObservationAdmin, VideoAdmin)
from .models import (Site, Camera, PenguinCount, PenguinObservation,
                     Video, PenguinUser, GraphForm)


User = get_user_model()


class PenguinUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'),
         {'fields': ('is_active',
                     'is_superuser',
                     'is_staff',
                     'last_login')}),
        (_('Statistics'), {
         'fields': ('observation_count', 'completion_count')}),
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser',
        'is_staff',
        'is_active',
        'observation_count',
        'completion_count',
        'completion_hours')

    list_filter = ('is_superuser',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )

    def changelist_view(self, request, extra_context=None):
        context = {
        }
        context.update(extra_context or {})
        return super(PenguinUserAdmin, self).changelist_view(request, context)

    readonly_fields = ('last_login', 'observation_count', 'completion_count')

    def response_add(self, request, obj, post_url_continue=None):
        return super(PenguinUserAdmin, self).response_add(request, obj,
                                                          post_url_continue)


class MedianSQL(models.sql.aggregates.Aggregate):
    sql_function = 'median'


class Median(models.Aggregate):

    """

    Migration 0008 adds the following;-

    CREATE OR REPLACE FUNCTION _final_median(numeric[])
       RETURNS numeric AS
    $$
       SELECT AVG(val)
       FROM (
         SELECT val
         FROM unnest($1) val
         ORDER BY 1
         LIMIT  2 - MOD(array_upper($1, 1), 2)
         OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
       ) sub;
    $$
    LANGUAGE 'sql' IMMUTABLE;

    DROP AGGREGATE IF EXISTS median(numeric)

    CREATE AGGREGATE median(numeric) (
      SFUNC=array_append,
      STYPE=numeric[],
      FINALFUNC=_final_median,
      INITCOND='{}'
    );
    """

    name = 'Median'

    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = MedianSQL(col,
                              source=source,
                              is_summary=is_summary,
                              **self.extra)
        query.aggregates[alias] = aggregate


class PenguinSite(AdminSite):

    def has_permission(self, request):
        return request.user.is_active

    def index(self, request, extra_context=None):
        """
        Add some extra index context such as a dataset to graph.
        """
        today = Arrow.fromdatetime(now())
        last_year = today.replace(months=-11)

        site_dataset = OrderedDict()

        sites = []

        if request.user.is_superuser:
            sites = Site.objects.annotate(video_count=Count('camera__video'))
        else:
            sites = Site.objects.annotate(
                video_count=Count('camera__video')).filter(
                id__lte=2).exclude(
                pk=17)

        gf = GraphForm(request.GET)

        startd = last_year
        endd = today

        if gf.is_valid():
            startd = Arrow.fromdate(gf.cleaned_data['start_date'])
            endd = Arrow.fromdate(gf.cleaned_data['end_date'])

        difference = (endd - startd).days

        period = 'month'

        if difference < 31:
            period = 'day'
        elif difference < (30 * 6):
            period = 'week'
        else:
            period = 'month'

        # For every site, aggregate the average number of returning penguins
        # across the entire month. These calculations are the average over
        # the median number of penguins observed each day.

        site_dataset['Total Penguins'] = []
        for site in sites:
            site_dataset[site.name] = []
            for start, end in Arrow.span_range(period, startd, endd):
                average = site.penguincount_set.filter(
                    date__gte=start.date(), date__lte=end.date()
                ).aggregate(penguins=Avg('total_penguins'))
                site_dataset[site.name].append({
                    'date': start.date(),
                    'value': "%0.2f" % average['penguins'] if (average['penguins'] > 0) else 0.0
                })
                for item in site_dataset['Total Penguins']:
                    if item['date'] == start.date():
                        item['value'] = "%0.2f" % (float(
                            item['value']) + (average['penguins'] if (average['penguins'] > 0) else 0.0))
                        break
                else:
                    site_dataset['Total Penguins'].append({
                        'date': start.date(),
                        'value': "%0.2f" % average['penguins'] if (average['penguins'] > 0) else 0.0
                    })

        context = {
            'sites': sites,
            'site_dataset': site_dataset,
            'title': _("Penguin island sites"),
            'gform': gf,
        }
        context.update(extra_context or {})
        return super(PenguinSite, self).index(request, context)


site = PenguinSite()
site.register(PenguinUser, PenguinUserAdmin)
site.register(Site, SiteAdmin)
site.register(PenguinCount, PenguinCountAdmin)
site.register(PenguinObservation, PenguinObservationAdmin)
site.register(Video, VideoAdmin)
site.register(Camera, CameraAdmin)
