from datetime import date, time

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from observations.models import Camera, PenguinObservation, Video


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class PenguinsViewsTest(TestCase):
    client = Client()

    def setUp(self):
        # Superuser
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@email.com",
            first_name="Admin",
            last_name="User",
            password="test",
        )
        # Observer user
        observer_group = Group.objects.create(name="Observers")
        self.observer = User.objects.create_user(
            username="observer",
            email="observer@email.com",
            first_name="Observer",
            last_name="User",
            password="test",
        )
        self.observer.groups.add(observer_group)
        # Regular user, no permissions.
        self.user = User.objects.create_user(
            username="testuser",
            email="user@email.com",
            first_name="Test",
            last_name="User",
            password="test",
        )

    def test_homepage(self):
        url = reverse("observations:site_home")
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/site_home.html")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class StaticPageViewsTest(TestCase):
    client = Client()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@email.com", password="test")

    def test_help_page_renders(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:help_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/help_page.html")

    def test_privacy_page_renders(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:privacy_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/privacy_page.html")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class VideoListViewTest(TestCase):
    client = Client()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@email.com", password="test")
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

    def test_video_list_renders(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/video_list.html")

    def test_video_list_filter_by_camera(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_list"), {"camera_id": self.camera.pk})
        self.assertEqual(response.status_code, 200)

    def test_video_list_filter_by_date(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_list"), {"date": "2024-01-15"})
        self.assertEqual(response.status_code, 200)

    def test_video_list_filter_by_completed(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_list"), {"completed": "false"})
        self.assertEqual(response.status_code, 200)

    def test_video_list_filter_by_views(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_list"), {"views": "true"})
        self.assertEqual(response.status_code, 200)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class VideoDetailViewTest(TestCase):
    client = Client()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@email.com", password="test")
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

    def test_video_detail_renders(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_detail", kwargs={"pk": self.video.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/video_detail.html")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class VideoObservationsViewTest(TestCase):
    client = Client()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@email.com", password="test")
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
        PenguinObservation.objects.create(
            video=self.video,
            observer=self.user,
            position=100.0,
            count=3,
        )

    def test_video_observations_renders(self):
        self.client.login(username="testuser", password="test")
        response = self.client.get(reverse("observations:video_observations", kwargs={"pk": self.video.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/video_observations_table.html")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class PenguinObservationCreateViewTest(TestCase):
    client = Client()

    def setUp(self):
        observers_group = Group.objects.create(name="Observers")
        self.observer = User.objects.create_user(username="observer", email="observer@email.com", password="test")
        self.observer.groups.add(observers_group)
        self.regular_user = User.objects.create_user(username="regular", email="regular@email.com", password="test")
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

    def test_create_observation_requires_permission(self):
        self.client.login(username="regular", password="test")
        url = reverse("observations:penguinobservation_create", kwargs={"pk": self.video.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 403)

    def test_create_observation_success(self):
        self.client.login(username="observer", password="test")
        url = reverse("observations:penguinobservation_create", kwargs={"pk": self.video.pk})
        response = self.client.post(
            url,
            {
                "videoPosition": 120,
                "penguinCount": 5,
                "comments": "Five penguins",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PenguinObservation.objects.filter(video=self.video).count(), 1)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class VideoCompleteViewTest(TestCase):
    client = Client()

    def setUp(self):
        observers_group = Group.objects.create(name="Observers")
        self.observer = User.objects.create_user(username="observer", email="observer@email.com", password="test")
        self.observer.groups.add(observers_group)
        self.regular_user = User.objects.create_user(username="regular", email="regular@email.com", password="test")
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

    def test_video_complete_requires_permission(self):
        self.client.login(username="regular", password="test")
        url = reverse("observations:video_complete", kwargs={"pk": self.video.pk})
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, 403)

    def test_video_complete_success(self):
        self.client.login(username="observer", password="test")
        url = reverse("observations:video_complete", kwargs={"pk": self.video.pk})
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, 200)
        self.video.refresh_from_db()
        self.assertTrue(self.video.mark_complete)
