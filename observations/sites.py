from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from observations.admin import (SiteAdmin, CameraAdmin, PenguinCountAdmin,
                                PenguinObservationAdmin, VideoAdmin)
from observations.models import (Site, Camera, PenguinCount,
                                 PenguinObservation, Video)

from arrow import Arrow
import logging

logger = logging.getLogger(__name__)


class PenguinUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )

    readonly_fields = ('last_login',)

    def response_add(self, request, obj, post_url_continue=None):
        return super(UserAdmin, self).response_add(request, obj,
                                                   post_url_continue)

class PenguinSite(AdminSite):

    def has_permission(self, request):
        return request.user.is_active

    def index(self, request, extra_context=None):
        """
        Add some extra index context such as a dataset to graph.
        """
        today = Arrow.fromdatetime(now())
        last_year = today.replace(months=-11)

        site_dataset = {}
        # For every site, aggregate the average number of returning penguins
        # across the entire month. These calculations are the average over
        # the median number of penguins observed each day.
        for site in Site.objects.all():
            site_dataset[site.name] = []
            for start, end in Arrow.span_range('month', last_year, today):
                average = site.penguincount_set.filter(
                    date__gte=start.date(), date__lte=end.date()
                ).aggregate(penguins=Avg('total_penguins'))

                site_dataset[site.name].append({
                    'date': start.date(),
                    'value': "%0.2f" % average['penguins'] if average['penguins'] else 0
                })

        context = {
            'sites': Site.objects.all(),
            'site_dataset': site_dataset,
            'title': _("Penguin island sites")
        }
        context.update(extra_context or {})
        return super(PenguinSite, self).index(request, context)

site = PenguinSite()

site.register(User, PenguinUserAdmin)
site.register(Site, SiteAdmin)
site.register(PenguinCount, PenguinCountAdmin)
site.register(PenguinObservation, PenguinObservationAdmin)
site.register(Video, VideoAdmin)
site.register(Camera, CameraAdmin)
site.register(FlatPage, FlatPageAdmin)
#site.register()