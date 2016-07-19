# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.utils.encoding import force_str
from arrow import Arrow
import ephem
from rest_framework import mixins
from rest_framework.generics import SingleObjectAPIView
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


class RetrievePartialUpdateDestroyAPIView(PartialUpdateModelMixin,
                                          mixins.RetrieveModelMixin,
                                          mixins.UpdateModelMixin,
                                          mixins.DestroyModelMixin,
                                          SingleObjectAPIView):

    @property
    def allowed_methods(self):
        """
        Return the list of allowed HTTP methods, uppercased.
        """
        self.http_method_names.append("patch")
        return [method.upper() for method in self.http_method_names
                if hasattr(self, method)]

    def get_serializer(
            self,
            instance=None,
            data=None,
            files=None,
            partial=False):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        return serializer_class(
            instance,
            data=data,
            files=files,
            partial=partial,
            context=context)

    def patch(self, request, *args, **kwargs):
        return self.update_partial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
