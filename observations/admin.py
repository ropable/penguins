
from django.contrib.gis import admin
from django.contrib.gis.admin import ModelAdmin

from observations.models import Camera, Video, PenguinObservation


class CameraAdmin(ModelAdmin):
    list_display = ('name', 'camera_key', 'active')


class VideoAdmin(ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'camera', 'views', 'mark_complete')


class PenguinObservationAdmin(ModelAdmin):
    list_display = ('video', 'date', 'position', 'seen')


admin.site.register(Camera, CameraAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(PenguinObservation, PenguinObservationAdmin)
