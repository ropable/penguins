from django.contrib.gis import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import ModelAdmin
from django.contrib.gis.db import models
import mapwidgets

from observations.models import Camera, Video, PenguinObservation


class CameraAdmin(ModelAdmin):
    list_display = ("name", "camera_key", "active", "video_count", "newest_video")
    list_filter = ("active",)
    formfield_overrides = {
        models.PointField: {"widget": mapwidgets.LeafletPointFieldWidget}
    }

    def video_count(self, obj):
        return obj.video_set.count()

    def newest_video(self, obj):
        return obj.get_newest_video() or ""


class VideoAdmin(ModelAdmin):
    class MarkedCompleteFilter(SimpleListFilter):
        title = "marked complete"
        parameter_name = "mark_complete"

        def lookups(self, request, model_admin):
            return (
                ("true", "Yes"),
                ("false", "No"),
            )

        def queryset(self, request, queryset):
            if self.value():
                if self.value() == "true":
                    return queryset.filter(mark_complete=True)
                elif self.value() == "false":
                    return queryset.filter(mark_complete=False)

    date_hierarchy = "date"
    list_display = (
        "date",
        "start_time",
        "end_time",
        "camera",
        "views",
        "mark_complete",
    )
    list_filter = ("camera", MarkedCompleteFilter)
    readonly_fields = ("date", "camera", "file", "start_time", "end_time")
    filter_horizontal = ("completed_by",)
    fieldsets = (
        (
            "Video information",
            {
                "fields": (
                    "date",
                    "camera",
                    "file",
                    "start_time",
                    "end_time",
                )
            },
        ),
        (
            "Viewing information",
            {
                "fields": (
                    "views",
                    "mark_complete",
                    "completed_by",
                )
            },
        ),
    )


class PenguinObservationAdmin(ModelAdmin):
    date_hierarchy = "video__date"
    list_display = ("video", "position", "seen", "observer", "validated")
    list_filter = ("video__camera", "validated")
    readonly_fields = ("video", "observer", "position", "seen", "comments")
    fieldsets = (
        (
            "Observation information",
            {
                "fields": (
                    "video",
                    "observer",
                    "position",
                    "seen",
                    "comments",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "raining",
                    "validated",
                )
            },
        ),
    )


admin.site.register(Camera, CameraAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(PenguinObservation, PenguinObservationAdmin)
