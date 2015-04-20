from __future__ import unicode_literals

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguins.settings")

from django.utils import six

from observations.models import PenguinCount, Site, Camera

from collections import namedtuple
from datetime import datetime
from openpyxl import load_workbook

workbook = load_workbook(filename=r'import.xlsx', data_only=True)

sheet_ranges = workbook['2012-2013 CHY']

# Make a namedtuple for ease of access.
Observation = namedtuple('Observation',
                         ['observer', 'camera', 'date', 'day', 'month', 'year',
                          'civil_twilight', 'sub_fifteen', 'zero_to_fifteen',
                          'fifteen_to_thirty', 'thirty_to_fourty_five',
                          'fourty_five_to_sixty', 'sixty_to_seventy_five',
                          'seventy_five_to_ninety', 'total_penguins',
                          'comments'])

for row in sheet_ranges.rows:
    observation = Observation(*map(lambda x: x.value, row[:16]))

    if observation.observer is None or observation.observer == "Observer":
        # spurious, unneeded rows, skip.
        continue

    # We can get the site (Site 1 or Site 3) from the camera field. This
    # requires some hard-coded logic. The best kind of logic.
    if observation.camera == "North":
        site = Site.objects.get(name="Site 1")
        camera = Camera.objects.get(name="North Pole")
    elif observation.camera == "South":
        site = Site.objects.get(name="Site 3")
        camera = Camera.objects.get(name="South Pole")
    else:
        print("Couldn't find camera or site for observation on %s. Camera "
              "was: %s" % (observation.date, observation.camera))
        continue

    # Check if the any of the count columns contain "n/a". If so, set the
    # reading to zero (the comments usually reference the problem).
    readings = {
        'sub_fifteen': observation.sub_fifteen,
        'zero_to_fifteen': observation.zero_to_fifteen,
        'fifteen_to_thirty': observation.fifteen_to_thirty,
        'thirty_to_fourty_five': observation.thirty_to_fourty_five,
        'fourty_five_to_sixty': observation.fourty_five_to_sixty,
        'sixty_to_seventy_five': observation.sixty_to_seventy_five,
        'seventy_five_to_ninety': observation.seventy_five_to_ninety,
        'total_penguins': observation.total_penguins
    }

    for key, value in readings.items():
        if isinstance(value, six.string_types) and value.strip() == "n/a":
            readings[key] = 0

    try:
        # If an object already exists for this date, skip adding it. Before
        # running the import script we need to be sure that the database is
        # emptied of any already-entered data.
        obj = PenguinCount.objects.get(site=site, date=observation.date)
    except PenguinCount.DoesNotExist:
        # Nothing exists for this date yet, add a new entry.
        civil_twilight = datetime.combine(observation.date.date(),
                                          observation.civil_twilight)
        date = observation.date.date(),
        obj = PenguinCount.objects.create(site=site,
            date=observation.date.date(), comments=observation.comments,
            civil_twilight=civil_twilight, sub_fifteen=readings['sub_fifteen'],
            zero_to_fifteen=readings['zero_to_fifteen'],
            fifteen_to_thirty=readings['fifteen_to_thirty'],
            thirty_to_fourty_five=readings['thirty_to_fourty_five'],
            fourty_five_to_sixty=readings['fourty_five_to_sixty'],
            sixty_to_seventy_five=readings['sixty_to_seventy_five'],
            seventy_five_to_ninety=readings['seventy_five_to_ninety'],
            total_penguins=readings['total_penguins'])
