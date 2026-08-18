from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone

from observations.models import Camera, PenguinObservation, Video


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class CameraModelTest(TestCase):
    def setUp(self):
        self.camera = Camera.objects.create(
            name="Test Camera",
            camera_key="test-key",
            location=Point(115.695, -32.305, srid=4326),
            active=True,
        )

    def test_str_active(self):
        self.assertEqual(str(self.camera), "Test Camera")

    def test_str_inactive(self):
        self.camera.active = False
        self.assertEqual(str(self.camera), "Test Camera (inactive)")

    def test_get_newest_video_no_videos(self):
        self.assertIsNone(self.camera.get_newest_video())

    def test_get_newest_video_returns_newest(self):
        Video.objects.create(
            date=date(2024, 1, 1),
            camera=self.camera,
            uploaded_file=ContentFile(b"older", name="older.mp4"),
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        newer = Video.objects.create(
            date=date(2024, 1, 2),
            camera=self.camera,
            uploaded_file=ContentFile(b"newer", name="newer.mp4"),
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        self.assertEqual(self.camera.get_newest_video(), newer)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class VideoModelTest(TestCase):
    def setUp(self):
        self.camera = Camera.objects.create(
            name="Test Camera",
            camera_key="test-key",
            location=Point(115.695, -32.305, srid=4326),
        )
        self.video = Video.objects.create(
            date=date(2024, 1, 15),
            camera=self.camera,
            uploaded_file=ContentFile(b"video", name="videos/test_video.mp4"),
            start_time=time(8, 0),
            end_time=time(9, 0),
            views=3,
        )

    def test_str(self):
        self.assertIn("Test Camera", str(self.video))
        self.assertIn("2024-01-15", str(self.video))

    def test_get_absolute_url(self):
        self.assertEqual(self.video.get_absolute_url(), f"/videos/{self.video.pk}/")

    def test_get_video_filename(self):
        filename = self.video.uploaded_file.name.split("/")[-1]
        self.assertEqual(self.video.get_video_filename(), filename)

    def test_get_content_disposition(self):
        filename = self.video.uploaded_file.name.split("/")[-1]
        self.assertEqual(self.video.get_content_disposition(), f"attachment; filename={filename}")

    def test_duration(self):
        self.assertEqual(self.video.duration, timedelta(hours=1))

    def test_get_start_datetime(self):
        start = self.video.get_start_datetime()
        self.assertEqual(start.date(), self.video.date)
        self.assertEqual(start.time(), self.video.start_time)

    def test_clean_date_rejects_future(self):
        from django.forms import ValidationError

        self.video.date = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.video.clean_date()

    def test_clean_end_time_rejects_before_start(self):
        from django.forms import ValidationError

        self.video.end_time = time(7, 0)
        with self.assertRaises(ValidationError):
            self.video.clean_end_time()


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class PenguinObservationModelTest(TestCase):
    def setUp(self):
        self.camera = Camera.objects.create(
            name="Test Camera",
            camera_key="test-key",
            location=Point(115.695, -32.305, srid=4326),
        )
        self.video = Video.objects.create(
            date=date(2024, 1, 15),
            camera=self.camera,
            uploaded_file=ContentFile(b"video", name="test.mp4"),
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        self.observer = User.objects.create_user(username="observer", password="test")
        self.observation = PenguinObservation.objects.create(
            video=self.video,
            observer=self.observer,
            position=300.0,
            count=5,
            comments="Five penguins",
        )

    def test_str(self):
        obs_str = str(self.observation)
        self.assertIn("5", obs_str)
        self.assertIn("Test Camera", obs_str)
        self.assertIn(str(self.observer), obs_str)

    def test_get_observation_datetime(self):
        dt = self.observation.get_observation_datetime()
        expected = timezone.make_aware(datetime.combine(self.video.date, self.video.start_time) + timedelta(seconds=300))
        self.assertEqual(dt, expected)
