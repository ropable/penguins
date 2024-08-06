from django.urls import path

from observations import views

urlpatterns = [
    path("help/", views.HelpPage.as_view(), name="help_page"),
    path("", views.SiteHome.as_view(), name="site_home"),
]
