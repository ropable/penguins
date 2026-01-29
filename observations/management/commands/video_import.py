import logging
import re
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from storages.backends.azure_storage import AzureStorage

from observations.models import Camera, Video


class Command(BaseCommand):
    help = "Imports outstanding encoded videos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            action="store",
            type=str,
            dest="year",
            help="Calendar year for video import (optional, defaults to current year)",
        )

    def handle(self, *args, **options):
        logger = logging.getLogger("penguins")
        logger.info("Starting import of encoded videos")

        if options["year"]:
            # Validate the passed-in year value.
            try:
                datetime.strptime(options["year"], "%Y")
                year = options["year"]
            except ValueError:
                logger.warning(f"Unable to parse value {options['year']} as calendar year")
                return
        else:
            year = date.today().year

        logger.info(f"Querying uploaded videos in Azure for {year}")
        store = AzureStorage()

        # Historically, all videos (blobs) are saved with the prefix path `beach_return_cams_2`.
        # Filter the response to only those blobs for the current year.
        prefix = f"beach_return_cams_2/{year}"
        all_blobs = [name for name in store.client.list_blob_names(name_starts_with=prefix) if name.endswith(".mp4")]
        count = 0
        pattern = re.compile(r"^([-\d]+)_([-\d]+)_(.+)$")

        logger.info("Checking for unpublished videos")
        for blob in all_blobs:
            if Video.objects.filter(uploaded_file=blob).exists():
                continue
            # Final segment of the blob name e.g 2024-08-20_1700_South.mp4
            video_filename = blob.split("/")[-1]

            # Parse the start_time string.
            timestamp = video_filename[0:13]  # Eg.g. 2024-08-20_17
            try:
                video_datetime = datetime.strptime(timestamp, "%Y-%m-%d_%H")
            except:
                logger.warning("Unable to parse timestamp from {}".format(video_filename))
                continue

            # Parse camera name and find matches. There are three capture groups in the regex,
            # therefore each matches consists of a list containing one tuple containing matches
            # e.g. [('2024-08-20', '1700', 'South.mp4')]
            matches = re.findall(pattern, video_filename)
            if not matches:
                continue

            camera = matches[0][2]  # Examples: South.mp4, t1_south_pole.mp4
            camera_key = camera.split(".")[0]  # Examples: South, t1_south_pole
            if Camera.objects.filter(camera_key__icontains=camera_key).exists():
                camera = Camera.objects.filter(camera_key__icontains=camera_key).first()
            else:
                camera = None

            if not camera:
                logger.warning("No matching camera found, skipping video: {}".format(video_filename))

            if video_datetime and camera:
                Video.objects.create(
                    date=video_datetime.date(),
                    start_time=video_datetime.time(),
                    end_time=(video_datetime + timedelta(hours=1)).time(),
                    camera=camera,
                    uploaded_file=blob,
                )

                count += 1
        logger.info("Import task completed, {} videos imported".format(count))
