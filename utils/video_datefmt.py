import os
from django.conf import settings

import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'penguins.settings'
from django.contrib.auth import get_user_model
from observations.models import *

from dateutil import tz
import datetime

def printTest():
        print('Shell Test')


def video_names():
    """
    Script to change video file names from %d-%m-%Y to %Y-%m-%d
    """

    videos = Video.objects.all()
    for video in videos:
        #folder=video.file.name.split('/')[0]
        new_folder = 'beach_return_cams_2'
        nameparts=video.file.name.split('/')[1].split('_')
        new_datefmt = '-'.join(nameparts[0].split('-')[::-1])
        #import ipdb; ipdb.set_trace()
        if len(new_datefmt.split('-')[0]) == 4: # new fmt should have first item as YEAR
            video.file.name = new_name = new_folder + os.sep + new_datefmt + '_' + '_'.join(nameparts[1:])
            video.save()
            print ('New Name {}'.format(video.file.name))
        else:
            print ('Already in New Format {}'.format(video.file.name))


