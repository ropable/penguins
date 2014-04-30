# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_str

from arrow import Arrow

import ephem


def civil_twilight(date, lon, lat):
    """
    Returns the evening civil twilight time as a `datetime.datetime` in UTC.
    Takes the date to calculate for (as a `datetime.date`), and the longitude
    and lattitude of the location.

    Evening civil twilight is defined as ending when the geometric centre of
    the sun is 6° below the horizon.
    """
    location = ephem.Observer()
    location.date = date.strftime("%Y/%m/%d")
    location.lon = force_str(lon)
    location.lat = force_str(lat)
    location.horizon = force_str("-6")

    twilight = location.next_setting(ephem.Sun(), use_center=True)
    return Arrow.fromdatetime(twilight.datetime()).datetime
