from __future__ import unicode_literals, absolute_import

from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, BaseUserManager, Group
from django.contrib.gis.db import models as geo_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetimewidget.widgets import DateWidget
from django import forms

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from observations.utils import civil_twilight
import datetime
import logging
import os



logger = logging.getLogger(__name__)


class ObservationBase(models.Model):
    """
    TODO
    This class can be replaced if inheriting from
    swingers.models.auth.Audit. clean_field() method below is from there.
    """

    def clean_fields(self, exclude=None):
        """
        Override clean_fields to do what model validation should have done
        in the first place -- call clean_FIELD during model validation.
        """
        errors = {}

        for f in self._meta.fields:
            if f.name in exclude:
                continue
            if hasattr(self, "clean_%s" % f.attname):
                try:
                    getattr(self, "clean_%s" % f.attname)()
                except ValidationError as e:
                    # TODO: Django 1.6 introduces new features to
                    # ValidationError class, update it to use e.error_list
                    errors[f.name] = e.messages

        try:
            super(ObservationBase, self).clean_fields(exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True

class PenguinUserManager(BaseUserManager):
    def __init__(self):
        super(BaseUserManager, self).__init__()
        #self.model = PenguinUser


class PenguinUser(AbstractUser):

    @property
    def completion_count(self):
        return self.videos_seen.count()

    @property
    def observation_count(self):
        return self.observations.count()

    @property
    def completion_hours(self):
        from datetime import timedelta
        t = timedelta()
        for i in self.videos_seen.all():
            t += i.duration
        return t

    #objects = PenguinUserManager()

    class Meta:
        db_table = 'auth_user' #Leave it alone!
        managed = False


@python_2_unicode_compatible
class Site(geo_models.Model):
    """
    Represents a site that observations are recorded. It may or may not
    have multiple cameras associated with it.
    """
    name = models.CharField(max_length=100)
    location = geo_models.PointField()

    def __str__(self):
        if  self.camera_set.count() > 0:
            return "{} ({})".format( self.name, ', '.join([c.name.encode("ascii") for c in self.camera_set.all()]) )
        else: return self.name
    class Meta:
        ordering = ['name']


@python_2_unicode_compatible
class Camera(models.Model):
    """
    A camera represents a single recording device at one of the sites that
    penguin observations are to be recorded.
    """
    name = models.CharField(max_length=100)
    camera_key = models.CharField(max_length=100,default='')
    site = models.ForeignKey(Site, blank=True, null=True)
    ip_address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PenguinCount(ObservationBase):
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
        if self.date > datetime.date.today():
            raise ValidationError("The 'Date' cannot be in the future!")

    def clean_civil_twilight(self):
        if self.civil_twilight is None:
            raise ValidationError("This field is required!")
        if self.civil_twilight > timezone.now():
            raise ValidationError("The 'Civil Twilight Date' cannot be in the future!")

    def __str__(self):
        return "%s" % self.date

    class Meta:
        ordering = ['-date']

@python_2_unicode_compatible
class Video(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True,default="")
    date = models.DateField(_("Date"),
        help_text=_("The date of the recording."))
    camera = models.ForeignKey(Camera)
    file = models.FileField(upload_to='videos/')
    start_time = models.TimeField(_("Start time"),
        help_text=_("The start time of the recording."))
    end_time = models.TimeField(_("End time"),
        help_text=_("The end time of the recording (usually 1h after start)."))
    views = models.IntegerField(default=0)
    mark_complete = models.BooleanField(default=False,help_text=_("Has this been viewed in its entirety by a reviewer"))
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name="videos_seen",verbose_name="Users who have seen this video")

    def clean_date(self):
        if self.date > datetime.date.today():
            raise ValidationError("The 'Date' cannot be in the future!")

    def clean_end_time(self):
        if self.end_time < self.start_time:
            raise ValidationError("The 'End Time' cannot be before the 'Start Time'!")

    @property
    def duration(self):
        from datetime import timedelta
        end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute, seconds=self.end_time.second)
        start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute, seconds=self.start_time.second)
        return end - start

    def __str__(self):
        return "%s - %s @ %s" % (self.camera.name, self.name, str(self.date))

    @classmethod
    def import_folder(cls, folder=settings.S3_FOLDER):
        logger = logging.getLogger('videos')
        logger.debug('Started import_folder method.')
        VIDEO_FORMATS = ('.mp4', '.avi', '.mkv')
        videos = [v for v in default_storage.listdir(folder)[1] if v.endswith(VIDEO_FORMATS)]
        count = 0
        for video in videos:
            logger.debug("Checking {0}".format(video))
            nameparts = video.split("_", 3)
            #if len(nameparts) != 2:
            #    logger.debug("Error: can't parse {0}".format(nameparts))
            #    continue
            filename = os.path.join(folder, video)
            if cls.objects.filter(file=filename).exists():
                continue
            # If video doesn't exist and filename splits nicely, create it.
            logger.debug("Importing {0}".format(video))
            datestr = '_'.join(nameparts[0:2])
            try:
                video_datetime = datetime.datetime.strptime(datestr, "%Y-%m-%d_%H")
            except:
                datestr = '_'.join(nameparts[0:1])
                video_datetime = datetime.datetime.strptime(datestr, "%Y-%m-%d")
            date = video_datetime.date()
            start_time = video_datetime.time()
            camstr = nameparts[-1]
            camstr = camstr.split(".")[0]  # Remove the extension.
            # assume each video is 60 mins long (video times are inaccurate/halved?)
            end_time = (video_datetime + datetime.timedelta(minutes=60)).time()
            logger.debug("Finding camera name closest to {} str:{}*".format(camstr,camstr.split("_")[0]))
            try:
                camera = Camera.objects.filter(camera_key__icontains=camstr.split("_")[0])[0] #use filter()[0] rather than get if theres dupes in the db.
                cls.objects.create(date=date, start_time=start_time, end_time=end_time,
                                   camera=camera, file=os.path.join(folder, video))
                count += 1
            except:
                logger.error('No matching camera found, skipping video name {}'.format(nameparts[-1]))

        logger.debug("Import task completed.")
        return count

    class Meta:
        ordering = ['-date']


@python_2_unicode_compatible
class PenguinVideoObservation(models.Model):
    video = models.ForeignKey(Video)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "<seen in %s> (%s-%s)" % (
            self.video.name, self.start_time, self.end_time)


@python_2_unicode_compatible
class PenguinObservation(ObservationBase):
    DIRECTION_CHOICES = (
        (1, _("N")),
        (2, _("NNW")),
        (3, _("NW")),
        (4, _("WNW")),
        (5, _("W")),
        (6, _("WSW")),
        (7, _("SW")),
        (8, _("SSW")),
        (9, _("S")),
        (10, _("SSE")),
        (11, _("SE")),
        (12, _("ESE")),
        (13, _("E")),
        (14, _("ENE")),
        (15, _("NE")),
        (16, _("NNE")),
    )

    PHASE_CHOICES = (
        (1, _("Full")),
        (2, _("First quarter")),
        (3, _("Half")),
        (4, _("Third quarter")),
        (5, _("New")),
    )

    date = models.DateTimeField(default=timezone.now)
    site = models.ForeignKey(Site)
    camera = models.ForeignKey(Camera, blank=True, null=True)
    observer = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="observations")
    seen = models.PositiveSmallIntegerField(verbose_name='count',
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    comments = models.TextField(blank=True, null=True)
    wind_direction = models.PositiveSmallIntegerField(choices=DIRECTION_CHOICES,
        verbose_name=_("Wind direction"), blank=True, null=True)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1,
        verbose_name=_("Wind speed (km/h)"), blank=True, null=True)
    wave_direction = models.PositiveSmallIntegerField(choices=DIRECTION_CHOICES,
        verbose_name=_("Wave direction"), blank=True, null=True)
    wave_height = models.DecimalField(max_digits=4, decimal_places=1,
        verbose_name=_("Wave height (m)"), blank=True, null=True)
    wave_period = models.PositiveSmallIntegerField(
        verbose_name=_("Wave period (s)"), blank=True, null=True)
    moon_phase = models.PositiveSmallIntegerField(choices=PHASE_CHOICES,
        verbose_name=_("Moon phase"), blank=True, null=True)
    raining = models.BooleanField(_("Raining?"), default=False,
        help_text=_("Was it raining at the time of the observation?"))
    position = models.FloatField(default=0,null=True,verbose_name=_("Position in video"))
    video = models.ForeignKey(Video,default=None,null=True,verbose_name=_("Video filename"))
    validated = models.BooleanField(default=True,verbose_name=_('Confirmed'))
    def clean_date(self):
        if self.date > timezone.now():
            raise ValidationError("The 'Date' cannot be in the future!")

    def __str__(self):
        return "%s penguins seen on %s by %s" % (
            self.seen, self.date, self.observer)


class ObserverCounter:
    def __init__(self):
        self.total = 0
        self.timestamps ={}
        for x in xrange(0,10):
            self.timestamps[x] = 0


@receiver(pre_delete, sender=PenguinObservation)
def trigger_recount_prior_to_delete(sender, instance, **kwargs):
    instance.seen = 0
    instance.save() #TRIGGER THE APOCALYPSE


@receiver(post_save, sender=PenguinObservation)
def update_penguin_count(sender, instance, created, **kwargs):
    """
    Loop over all penguin observations for a particular day and update the
    count, and bucket them relative to the civil twilight time.
    """
    print "Pre-save observation interceptor triggered"
    penguin_count, new_count = PenguinCount.objects.get_or_create(
        date=instance.date.date(), site=instance.site)
    if new_count:
        penguin_count.civil_twilight = civil_twilight(instance.date.date(),
            instance.site.location.x, instance.site.location.y)
    date = instance.date.date()
    observations = PenguinObservation.objects.filter(seen__gt=0,
                    site=instance.site, validated = True,
        date__range=(datetime.datetime.combine(date, datetime.time.min),
                     datetime.datetime.combine(date, datetime.time.max)))
    observers = {}
    for o in observations.distinct('observer'):
        observers[o.observer.pk] = ObserverCounter()
        user_observations = observations.filter(observer=o.observer)
        for observation in user_observations:
            offset = observation.date - penguin_count.civil_twilight
            offset = offset.total_seconds() / 60  # in minutes
            range_pointer = int(offset /15) + 1
            if range_pointer >= 0 and range_pointer <= 9:
                observers[o.observer.pk].timestamps[range_pointer] += observation.seen
            else:
                observers[o.observer.pk].timestamps[9] += observation.seen
            observers[o.observer.pk].total = sum(observers[o.observer.pk].timestamps.values())
    range_iiterator = xrange(0,10)
    time_stamp = {}
    for r in range_iiterator:
        rangelist = []
        for k,o in observers.items():
            rangelist.append(o.timestamps[r])
        even = (0 if len(rangelist) % 2 else 1) + 1
        half = (len(rangelist) - 1) / 2
        time_stamp[r] = sum(sorted(rangelist)[half:half + even]) / float(even)
    # Denormalize...
    penguin_count.sub_fifteen = time_stamp[0]
    penguin_count.zero_to_fifteen = time_stamp[1]
    penguin_count.fifteen_to_thirty = time_stamp[2]
    penguin_count.thirty_to_fourty_five = time_stamp[3]
    penguin_count.fourty_five_to_sixty = time_stamp[4]
    penguin_count.sixty_to_seventy_five = time_stamp[5]
    penguin_count.seventy_five_to_ninety = time_stamp[6]
    penguin_count.ninety_to_one_oh_five = time_stamp[7]
    penguin_count.one_oh_five_to_one_twenty = time_stamp[8]
    penguin_count.outlier = time_stamp[9]
    penguin_count.total_penguins=sum(time_stamp.values())
    penguin_count.save()

@receiver(post_save, sender=User)
def update_user(sender, instance, created, **kwargs):
    if created:
        group, created = Group.objects.get_or_create(name="Observers")
        instance.is_staff = True
        instance.groups.add(group)
        instance.save()


class GraphForm(forms.Form):
#    'format': 'dd/mm/yyyy HH:ii P',
    start_date = forms.DateField(widget=DateWidget(attrs={'id':"startTime",'width':'45%'}, usel10n = False, bootstrap_version=3))
    end_date = forms.DateField(widget= DateWidget(attrs={'id':"endTime"}, usel10n = False, bootstrap_version=3))


    def clean(self):
        cleaned_data = super(GraphForm,self).clean()


        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if not start:
            self._errors['start_date']=self.error_class(["Please enter a start date"])
        if not end:
            self._errors['end_date']=self.error_class(["Please enter an end date"])

        if start and end and (end <= start):
            raise forms.ValidationError ("The end date is before the start date!")
        return cleaned_data
