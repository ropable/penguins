from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.test import TestCase

from penguins.utils import breadcrumbs_html, get_next_pages, get_previous_pages, user_can_add_observations


class PaginationUtilsTest(TestCase):
    def setUp(self):
        items = list(range(1, 26))  # 25 items -> 3 pages of 10
        paginator = Paginator(items, 10)
        self.page_1 = paginator.page(1)
        self.page_2 = paginator.page(2)
        self.page_3 = paginator.page(3)

    def test_get_previous_pages_first_page(self):
        self.assertEqual(get_previous_pages(self.page_1), [])

    def test_get_previous_pages_middle_page(self):
        self.assertEqual(get_previous_pages(self.page_2), [1])

    def test_get_previous_pages_count_limit(self):
        # Page 3 has only pages 1 and 2 before it.
        self.assertEqual(get_previous_pages(self.page_3, count=3), [1, 2])

    def test_get_next_pages_last_page(self):
        self.assertEqual(get_next_pages(self.page_3), [])

    def test_get_next_pages_middle_page(self):
        self.assertEqual(get_next_pages(self.page_2), [3])

    def test_get_next_pages_count_limit(self):
        # Page 1 has pages 2 and 3 after it.
        self.assertEqual(get_next_pages(self.page_1, count=3), [2, 3])


class UserCanAddObservationsTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="test"
        )
        self.observer = User.objects.create_user(
            username="observer", email="observer@example.com", password="test"
        )
        observers_group = Group.objects.create(name="Observers")
        self.observer.groups.add(observers_group)
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="test"
        )

    def test_superuser_can_add_observations(self):
        self.assertTrue(user_can_add_observations(self.superuser))

    def test_observer_can_add_observations(self):
        self.assertTrue(user_can_add_observations(self.observer))

    def test_regular_user_cannot_add_observations(self):
        self.assertFalse(user_can_add_observations(self.regular_user))

    def test_anonymous_user_cannot_add_observations(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(user_can_add_observations(AnonymousUser()))


class BreadcrumbsHtmlTest(TestCase):
    def test_single_active_link(self):
        links = [(None, "Home")]
        html = breadcrumbs_html(links)
        self.assertIn("Home", html)
        self.assertIn('class="breadcrumb-item active"', html)

    def test_multiple_links(self):
        links = [("/home/", "Home"), (None, "Videos")]
        html = breadcrumbs_html(links)
        self.assertIn("Home", html)
        self.assertIn("Videos", html)
        self.assertIn('href="/home/"', html)

    def test_active_link_has_no_href(self):
        links = [("/home/", "Home"), (None, "Videos")]
        html = breadcrumbs_html(links)
        # The active (last) item should use a <span>, not an <a>.
        self.assertIn('class="breadcrumb-item active"', html)
        self.assertIn("<span>Videos</span>", html)
