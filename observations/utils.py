# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.utils.encoding import force_str
from arrow import Arrow
import ephem
from rest_framework import status
from rest_framework.response import Response


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


class PartialUpdateModelMixin(object):

    """
    Update a model instance.
    Should be mixed in with `SingleObjectBaseView`.
    """

    def update_partial(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            created = False
        except Http404:
            self.object = None
            created = True

        serializer = self.get_serializer(
            self.object,
            data=request.DATA,
            files=request.FILES,
            partial=True)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save()
            status_code = created and status.HTTP_201_CREATED or status.HTTP_200_OK
            return Response(serializer.data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
