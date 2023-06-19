from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
import logging
from storages.backends.azure_storage import AzureStorage

from observations.models import Video, Camera


class Command(BaseCommand):
    help = 'Imports outstanding encoded videos'

    def handle(self, *args, **options):
        logger = logging.getLogger('observations')
        logger.info('Starting import of encoded videos')

        store = AzureStorage()
        all_blobs = store.list_all()
        video_formats = ('.mp4',)
        video_paths = [blob for blob in all_blobs if blob.endswith(video_formats)]
        count = 0

        for path in video_paths:
            if Video.objects.filter(file=path).exists():
                continue
            video_filename = path.split('/')[-1]  # Final segment of the path.

            # Parse the start_time string.
            timestamp = video_filename[0:13]
            try:
                video_datetime = datetime.strptime(timestamp, "%Y-%m-%d_%H")
            except:
                video_datetime = None

            # Parse camera name and find matching object
            camera_key = video_filename[17:-4].split("_")[0]
            if Camera.objects.filter(camera_key__icontains=camera_key).exists():
                camera = Camera.objects.filter(camera_key__icontains=camera_key).first()
            else:
                camera = None

            if not video_datetime:
                logger.warning('Unable to parse timestamp from {}'.format(video_filename))
            if not camera:
                logger.warning('No matching camera found, skipping video: {}'.format(video_filename))

            if video_datetime and camera:
                print("Importing {} for camera {}, date {}".format(video_filename, camera, video_datetime))
                Video.objects.create(
                    date=video_datetime.date(),
                    start_time=video_datetime.time(),
                    end_time=(video_datetime + timedelta(hours=1)).time(),
                    camera=camera,
                    file=path,
                )

                count += 1
        logger.info("Task completed, {} videos imported".format(count))
