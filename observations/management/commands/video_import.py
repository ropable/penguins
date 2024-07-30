from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
import logging
import re
from storages.backends.azure_storage import AzureStorage

from observations.models import Video, Camera


class Command(BaseCommand):
    help = 'Imports outstanding encoded videos'

    def handle(self, *args, **options):
        logger = logging.getLogger('observations')
        logger.info('Starting import of encoded videos')

        logger.info('Querying uploaded videos in Azure')
        store = AzureStorage()
        all_blobs = store.list_all()
        video_formats = ('.mp4',)
        video_paths = [blob for blob in all_blobs if blob.endswith(video_formats)]
        count = 0
        pattern = '^([-\d]+)_([-\d]+)_(.+)$'

        logger.info('Checking for unpublished videos')
        for path in video_paths:
            if Video.objects.filter(file=path).exists():
                continue
            video_filename = path.split('/')[-1]  # Final segment of the path.

            # Parse the start_time string.
            timestamp = video_filename[0:13]
            try:
                video_datetime = datetime.strptime(timestamp, "%Y-%m-%d_%H")
            except:
                logger.warning('Unable to parse timestamp from {}'.format(video_filename))
                continue

            # Parse camera name and find matching object
            matches = re.findall(pattern, video_filename)[0]  # Returns the tuple of matches.
            camera = matches[2]  # Examples: North.mp4, t1_south_pole.mp4
            camera_key = camera.split(".")[0]  # Examples: North, t1_south_pole
            if Camera.objects.filter(camera_key__icontains=camera_key).exists():
                camera = Camera.objects.filter(camera_key__icontains=camera_key).first()
            else:
                camera = None

            if not camera:
                logger.warning('No matching camera found, skipping video: {}'.format(video_filename))

            if video_datetime and camera:
                Video.objects.create(
                    date=video_datetime.date(),
                    start_time=video_datetime.time(),
                    end_time=(video_datetime + timedelta(hours=1)).time(),
                    camera=camera,
                    file=path,
                )

                count += 1
        logger.info('Import task completed, {} videos imported'.format(count))
