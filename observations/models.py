from __future__ import unicode_literals, absolute_import

from datetime import datetime, date, timedelta
from datetimewidget.widgets import DateWidget
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
#from django.db.models.signals import post_save, pre_delete
#from django.dispatch import receiver
from django.forms import ValidationError
#from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django import forms
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser

#from observations.utils import civil_twilight


class PenguinUser(AbstractUser):
    """Override the stock Django User model, because we didn't know better at the time.
    """
    class Meta:
        db_table = 'auth_user'  # Leave it alone!
        managed = False

    @property
    def completion_count(self):
        return self.videos_seen.count()

    @property
    def observation_count(self):
        return self.observations.count()

    @property
    def completion_hours(self):
        t = timedelta()
        for i in self.videos_seen.all():
            t += i.duration
        return t

    def is_observer(self):
        return 'Observers' in self.groups.values_list('name', flat=True)


@python_2_unicode_compatible
class Site(models.Model):
    """Represents a site that observations are recorded. It may or may not
    have multiple cameras associated with it.
    TODO: deprecate this model.
    """
    name = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        if self.camera_set.count() > 0:
            return "{} ({})".format(
                self.name, ', '.join([c.name for c in self.camera_set.all()]))
        else:
            return self.name

    class Meta:
        ordering = ['name']


@python_2_unicode_compatible
class Camera(models.Model):
    """A camera represents a single recording device at one of the sites that
    penguin observations are to be recorded.
    """
    name = models.CharField(max_length=100)
    camera_key = models.CharField(max_length=100, default="")  # Used to match camera to video recordings.
    site = models.ForeignKey(Site, blank=True, null=True)
    location = models.PointField(srid=4326, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.active:
            return self.name
        else:
            return '{} (inactive)'.format(self.name)

    def get_newest_video(self):
        """
        """
        video = Video.objects.filter(camera=self).first()  # Assumes ordering on Video.
        return video or None


@python_2_unicode_compatible
class PenguinCount(models.Model):
    """Represents an aggregation of penguin observations for a given date and site.
    TODO: Deprecate this model.
    """
    site = models.ForeignKey(Site)
    date = models.DateField(default=timezone.now)
    comments = models.TextField(null=True, blank=True)
    civil_twilight = models.DateTimeField(null=True, blank=True)
    sub_fifteen = models.DecimalField(
        _("-15-0"), default=0, max_digits=5, decimal_places=2)
    zero_to_fifteen = models.DecimalField(
        _("0-15"), default=0, max_digits=5, decimal_places=2)
    fifteen_to_thirty = models.DecimalField(
        _("15-30"), default=0, max_digits=5, decimal_places=2)
    thirty_to_fourty_five = models.DecimalField(
        _("30-45"), default=0, max_digits=5, decimal_places=2)
    fourty_five_to_sixty = models.DecimalField(
        _("45-60"), default=0, max_digits=5, decimal_places=2)
    sixty_to_seventy_five = models.DecimalField(
        _("60-75"), default=0, max_digits=5, decimal_places=2)
    seventy_five_to_ninety = models.DecimalField(
        _("75-90"), default=0, max_digits=5, decimal_places=2)
    ninety_to_one_oh_five = models.DecimalField(
        _("90-105"), default=0, max_digits=5, decimal_places=2)
    one_oh_five_to_one_twenty = models.DecimalField(
        _("105-120"), default=0, max_digits=5, decimal_places=2)
    total_penguins = models.DecimalField(
        _("total penguins"), default=0, max_digits=5, decimal_places=2)
    outlier = models.DecimalField(
        _("outlying times"), default=0, max_digits=5, decimal_places=2)

    def clean_date(self):
        if self.date > date.today():
            raise ValidationError("The 'Date' cannot be in the future!")

    def clean_civil_twilight(self):
        if self.civil_twilight is None:
            raise ValidationError("This field is required!")
        if self.civil_twilight > timezone.now():
            raise ValidationError(
                "The 'Civil Twilight Date' cannot be in the future!")

    def __str__(self):
        return str(self.date)

    class Meta:
        ordering = ["-date"]


@python_2_unicode_compatible
class Video(models.Model):
    """A video represents a single recording from a camera on Penguin Island, against which
    penguins will be counted. Normally videos are one hour duration.
    """
    date = models.DateField(help_text="The date of the recording.")
    camera = models.ForeignKey(Camera)
    file = models.FileField(upload_to="videos")
    start_time = models.TimeField(help_text="The start time of the recording.")
    end_time = models.TimeField(help_text="The end time of the recording (usually 1h after start).")
    views = models.PositiveSmallIntegerField(default=0)
    mark_complete = models.BooleanField(default=False, help_text="Has this been viewed in its entirety by a reviewer?")
    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="videos_seen", verbose_name="Users who have seen this video")

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return "{} @ {}".format(self.camera.name, str(self.date))

    def clean_date(self):
        if self.date > date.today():
            raise ValidationError("The 'Date' cannot be in the future!")

    def clean_end_time(self):
        if self.end_time < self.start_time:
            raise ValidationError(
                "The 'End Time' cannot be before the 'Start Time'!")

    @property
    def duration(self):
        end = timedelta(
            hours=self.end_time.hour,
            minutes=self.end_time.minute,
            seconds=self.end_time.second)
        start = timedelta(
            hours=self.start_time.hour,
            minutes=self.start_time.minute,
            seconds=self.start_time.second)
        return end - start

    def get_start_datetime(self):
        return datetime.combine(self.date, self.start_time)


@python_2_unicode_compatible
class PenguinObservation(models.Model):
    """Represents the observation of 0+ penguins at a particular frame within a video.
    More than one observation of the same penguins on the same video may exist, if >1 person
    watches the video and records an observation.
    """
    video = models.ForeignKey(Video)
    date = models.DateTimeField(help_text="The date on which the observation is noted")  # TODO: remove this field (use Video.date).
    observer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="observations")
    position = models.FloatField(
        default=0, null=True, verbose_name="Position (s)", help_text="Position in video (seconds from start)",
    )
    seen = models.PositiveSmallIntegerField(
        verbose_name="count", validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The count of penguins seen in this observation."
    )
    comments = models.TextField(blank=True, null=True)
    raining = models.BooleanField(default=False, help_text="Was it raining at the time of the observation?")
    validated = models.BooleanField(default=True, verbose_name="Confirmed")

    def __str__(self):
        return "{} penguin(s) seen on {} at {} by {}".format(self.seen, self.video.camera.name, self.get_observation_datetime(), self.observer)

    def get_observation_datetime(self):
        """From the associated video and the value of `position`, derive the datetime of the penguin observation.
        """
        start = datetime.combine(self.video.date, self.video.start_time).astimezone(timezone.get_current_timezone())
        return start + timedelta(seconds=self.position)


class ObserverCounter:

    def __init__(self):
        self.total = 0
        self.timestamps = {}
        for x in range(0, 10):
            self.timestamps[x] = 0


class GraphForm(forms.Form):
    start_date = forms.DateField(
        widget=DateWidget(
            attrs={
                'id': "startTime",
                'width': '45%'},
            usel10n=False,
            bootstrap_version=3))
    end_date = forms.DateField(
        widget=DateWidget(
            attrs={
                'id': "endTime"},
            usel10n=False,
            bootstrap_version=3))

    def clean(self):
        cleaned_data = super(GraphForm, self).clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if not start:
            self._errors['start_date'] = self.error_class(
                ["Please enter a start date"])
        if not end:
            self._errors['end_date'] = self.error_class(
                ["Please enter an end date"])
        if start and end and (end <= start):
            raise forms.ValidationError(
                "The end date is before the start date!")
        return cleaned_data
