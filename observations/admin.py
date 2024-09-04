from datetime import date, datetime
from django.contrib.gis import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import ModelAdmin
from django.contrib.gis.db import models
from django.http import HttpResponse
import mapwidgets
import xlsxwriter

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


@admin.action(description="Export selected record to XLSX")
def export_to_xlsx(modeladmin, request, queryset):
    """Writes a passed-in queryset of objects to a file-like object as an Excel spreadsheet."""
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f"attachment; filename=penguin_observations_{date.today().isoformat()}_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with xlsxwriter.Workbook(
        response,
        {
            "in_memory": True,
            "default_date_format": "dd-mmm-yyyy HH:MM",
            "remove_timezone": True,
        },
    ) as workbook:
        observations_sheet = workbook.add_worksheet("Penguin observations")
        observations_sheet.write_row(
            "A1",
            (
                "DATE",
                "CAMERA",
                "VIDEO",
                "OBSERVER",
                "SEEN (AWST)",
                "COUNT",
                "VALIDATED",
                "COMMENTS",
                "LINK",
            ),
        )
        row = 1

        for obj in queryset:
            observations_sheet.write_row(
                row,
                0,
                [
                    obj.video.date.strftime("%d/%b/%Y"),
                    obj.video.camera.__str__(),
                    obj.video.__str__(),
                    obj.observer.get_full_name(),
                    obj.get_observation_datetime().strftime("%d/%b/%Y %H:%M:%S"),
                    obj.seen,
                    obj.validated,
                    obj.comments,
                    request.build_absolute_uri(obj.video.get_absolute_url()),
                ],
            )
            row += 1

        observations_sheet.set_column("A:B", 12)
        observations_sheet.set_column("C:C", 38)
        observations_sheet.set_column("D:E", 24)
        observations_sheet.set_column("F:G", 12)
        observations_sheet.set_column("H:I", 40)

    return response


class PenguinObservationAdmin(ModelAdmin):
    actions = [export_to_xlsx]
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
