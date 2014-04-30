from __future__ import absolute_import

from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError

import os
import re
import subprocess

from datetime import datetime
from celery.utils.log import get_task_logger

from penguins.celery import app

from observations.models import Video, Camera

logger = get_task_logger(__name__)


@app.task
def convert_video(video_id):
    """
    Convert an MP4 video into WebM.
    """
    video = Video.objects.get(pk=video_id)
    logger.info("Converting video for %s and %s..." % (video.date,
                                                       video.start_time))
    path = os.path.join(settings.MEDIA_ROOT, video.file.name)
    cmd = ['ffmpeg', '-y', '-i', path, '-vcodec', 'libvpx',
           '-f', 'webm', path[:-4] + '.webm']
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except Exception as e:
        logger.info(e)


@app.task
def scheduler():
    """
    Check our incoming directory for any videos to add and then convert.
    """
    # If INCOMING_ROOT has been set, check it for any video files that can be
    # converted. Otherwise, do nothing.
    if settings.INCOMING_ROOT:
        logger.info("Checking for new videos...")
        for root, dirs, files in os.walk(settings.INCOMING_ROOT):
            for name in files:
                if name.endswith('.mov'):
                    # We found a video file to upload. Upload it and then
                    # schedule it for conversion.
                    match = re.match(r'(?P<date>\d+\-\d+\-\d+) (?P<time>\d+) '
                                     'TL (?P<camera>.*).mov', name)
                    path = os.path.join(root, name)

                    date = datetime.strptime(match.group('date'), "%d-%m-%Y")
                    start_time = match.group('time') + ':00:00'
                    end_time = match.group('time') + ':59:59'

                    # Try to retrieve the correct camera this video is
                    # attached to. If this fails, bail out.
                    try:
                        camera = Camera.objects.get(name=match.group('camera'))
                    except Camera.DoesNotExist:
                        logger.info("Couldn't find a camera attached to the "
                                    "video: %s" % name)
                        return

                    video_name = match.group('date')
                    video_file = open(path, 'rb')

                    # Check if a video object already exists for this file.
                    # If not, create one and schedule it for conversion.
                    try:
                        Video.objects.get(camera=camera, name=video_name,
                            date=date, start_time=start_time, end_time=end_time)
                    except Video.DoesNotExist:
                        video = Video.objects.create(camera=camera,
                            name=match.group('date'), date=date,
                            start_time=start_time, end_time=end_time,
                            file=File(video_file))

                        convert_video.delay(video.id)
