from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.contrib.gis.db import models as geo_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from observations.utils import civil_twilight
import datetime
import logging
import os

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Site(geo_models.Model):
    """
    Represents a site that observations are recorded. It may or may not
    have multiple cameras associated with it.
    """
    name = models.CharField(max_length=100)
    location = geo_models.PointField()

    def __str__(self):
        return "{} ({})".format( self.name, ', '.join([c.name.encode("ascii") for c in self.camera_set.all()]) )

    class Meta:
        ordering = ['name']


@python_2_unicode_compatible
class Camera(models.Model):
    """
    A camera represents a single recording device at one of the sites that
    penguin observations are to be recorded.
    """
    name = models.CharField(max_length=100)
    site = models.ForeignKey(Site, blank=True, null=True)
    ip_address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PenguinCount(models.Model):
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

    def __str__(self):
        return "%s" % self.date


@python_2_unicode_compatible
class Video(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(_("Date"),
        help_text=_("The date of the recording."))
    camera = models.ForeignKey(Camera)
    file = models.FileField(upload_to='videos/')
    start_time = models.TimeField(_("Start time"),
        help_text=_("The start time of the recording."))
    end_time = models.TimeField(_("End time"),
        help_text=_("The end time of the recording (usually 1h after start)."))
    views = models.IntegerField(default=0)

    def __str__(self):
        return "%s - %s" % (self.camera.name, self.name)

    @classmethod
    def import_folder(cls, folder="beach_return_cams"):
        videos = default_storage.listdir(folder)[1]
        for video in videos:
            print("checking {0}".format(video))
            nameparts = video.split("_tl_")
            if len(nameparts) != 2:
                print("can't parse {0}".format(nameparts))
                continue
            filename = os.path.join(folder, video)
            if cls.objects.filter(file=filename).exists():
                continue
            # If video doesn't exist, and filename splits nicely
            # create it
            print("importing {0}".format(video))
            datestr, camstr = nameparts
            camstr = camstr.split(".")[0]
            video_datetime = datetime.datetime.strptime(datestr, "%d-%m-%Y_%H")
            date = video_datetime.date()
            start_time = video_datetime.time()
            # assume each video is 60 mins long (video times are inaccurate/halved?)
            end_time = (video_datetime + datetime.timedelta(minutes=60)).time()
            print("Finding camera name closest to {}".format(camstr))
            camera = Camera.objects.get(name__istartswith=camstr.split("_")[0])
            cls.objects.create(date=date, start_time=start_time, end_time=end_time,
                               camera=camera, file=os.path.join(folder, video))

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
class PenguinObservation(models.Model):
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
    observer = models.ForeignKey(User)
    seen = models.PositiveSmallIntegerField(verbose_name='count',
        validators=[MinValueValidator(1), MaxValueValidator(100)])
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

    def __str__(self):
        return "%s penguins seen on %s by %s" % (
            self.seen, self.date, self.observer)


class ObserverCounter:
    def __init__(self):
        self.time_stamp_1 = []
        self.time_stamp_2 = []
        self.time_stamp_3 = []
        self.time_stamp_4 = []
        self.time_stamp_5 = []
        self.time_stamp_6 = []
        self.time_stamp_7 = []
        self.time_stamp_8 = []
        self.time_stamp_9 = []
        self.outlier_stamp = []
        self.total = 0


def calc_median(unsortedlist):
    sortedlist = sorted(unsortedlist)
    length = len(sortedlist)
    if length == 0:
        return 0
    if not length % 2:
        return (sortedlist[length / 2] + sortedlist[length / 2 - 1]) / 2
    return sortedlist[length / 2]


@receiver(post_save, sender=PenguinObservation)
def update_penguin_count(sender, instance, created, **kwargs):
    """
    Loop over all penguin observations for a particular day and update the
    count, and bucket them relative to the civil twilight time.
    """
    penguin_count, new_count = PenguinCount.objects.get_or_create(
        date=instance.date.date(), site=instance.site)

    if new_count:
        penguin_count.civil_twilight = civil_twilight(instance.date.date(),
            instance.site.location.x, instance.site.location.y)

    time_stamp_1 = 0
    time_stamp_2 = 0
    time_stamp_3 = 0
    time_stamp_4 = 0
    time_stamp_5 = 0
    time_stamp_6 = 0
    time_stamp_7 = 0
    time_stamp_8 = 0
    time_stamp_9 = 0
    outlier_stamp = 0
    total = 0

    # Get all the penguin observations in a particular day. This will be
    # easier to do once custom field lookups are implemented.
    date = instance.date.date()
    observations = PenguinObservation.objects.filter(
        date__range=(datetime.datetime.combine(date, datetime.time.min),
                     datetime.datetime.combine(date, datetime.time.max)))

    obslist = {}

    for observation in observations:
        if (observation.observer not in obslist):
            obslist[observation.observer] = ObserverCounter()
        logger.info(observation)
        offset = observation.date - penguin_count.civil_twilight
        offset = offset.total_seconds() / 60  # in minutes
        if (offset > -15 and offset < 0):
            obslist[observation.observer].time_stamp_1.append(observation.seen)
        if (offset >= 0 and offset < 15):
            obslist[observation.observer].time_stamp_2.append(observation.seen)
        if (offset >= 15 and offset < 30):
            obslist[observation.observer].time_stamp_3.append(observation.seen)
        if (offset >= 30 and offset < 45):
            obslist[observation.observer].time_stamp_4.append(observation.seen)
        if (offset >= 45 and offset < 60):
            obslist[observation.observer].time_stamp_5.append(observation.seen)
        if (offset >= 60 and offset < 75):
            obslist[observation.observer].time_stamp_6.append(observation.seen)
        if (offset >= 75 and offset < 90):
            obslist[observation.observer].time_stamp_7.append(observation.seen)
        if (offset >= 90 and offset < 105):
            obslist[observation.observer].time_stamp_8.append(observation.seen)
        if (offset >= 105 and offset < 120):
            obslist[observation.observer].time_stamp_9.append(observation.seen)
        if (offset < -15):
            obslist[observation.observer].outlier_stamp.append(observation.seen)
        if (offset > 120):
            obslist[observation.observer].outlier_stamp.append(observation.seen)
            #outlier
        obslist[observation.observer].total += observation.seen - calc_median(obslist[observation.observer].outlier_stamp)

    for k, v in obslist.items():
        v.time_stamp_1.sort()
        v.time_stamp_2.sort()
        v.time_stamp_3.sort()
        v.time_stamp_4.sort()
        v.time_stamp_5.sort()
        v.time_stamp_6.sort()
        v.time_stamp_7.sort()
        v.time_stamp_8.sort()
        v.time_stamp_9.sort()

        time_stamp_1 = calc_median(v.time_stamp_1)
        time_stamp_2 = calc_median(v.time_stamp_2)
        time_stamp_3 = calc_median(v.time_stamp_3)
        time_stamp_4 = calc_median(v.time_stamp_4)
        time_stamp_5 = calc_median(v.time_stamp_5)
        time_stamp_6 = calc_median(v.time_stamp_6)
        time_stamp_7 = calc_median(v.time_stamp_7)
        time_stamp_8 = calc_median(v.time_stamp_8)
        time_stamp_9 = calc_median(v.time_stamp_9)
        outlier_stamp = calc_median(v.outlier_stamp)

    total = (time_stamp_1 + time_stamp_2 + time_stamp_3 + time_stamp_4 + time_stamp_5 +
            time_stamp_6 + time_stamp_7 + time_stamp_8 + time_stamp_9)

    penguin_count.sub_fifteen = time_stamp_1
    penguin_count.zero_to_fifteen = time_stamp_2
    penguin_count.fifteen_to_thirty = time_stamp_3
    penguin_count.thirty_to_fourty_five = time_stamp_4
    penguin_count.fourty_five_to_sixty = time_stamp_5
    penguin_count.sixty_to_seventy_five = time_stamp_6
    penguin_count.seventy_five_to_ninety = time_stamp_7
    penguin_count.ninety_to_one_oh_five = time_stamp_8
    penguin_count.one_oh_five_to_one_twenty = time_stamp_9
    penguin_count.outlier = outlier_stamp

    penguin_count.total_penguins = (total)
    penguin_count.save()


@receiver(post_save, sender=User)
def update_user(sender, instance, created, **kwargs):
    if created:
        group, created = Group.objects.get_or_create(name="Observers")
        instance.is_staff = True
        instance.groups.add(group)
        instance.save()
