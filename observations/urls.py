from django.urls import path

from observations import views

app_name = "observations"
urlpatterns = [
    path("videos/", views.VideoList.as_view(), name="video_list"),
    path("videos/<int:pk>/", views.VideoDetail.as_view(), name="video_detail"),
    path("videos/<int:pk>/create-observation/", views.PenguinObservationCreate.as_view(), name="penguinobservation_create"),
    path("videos/<int:pk>/observations/", views.VideoObservations.as_view(), name="video_observations"),
    path("videos/<int:pk>/complete/", views.VideoComplete.as_view(), name="video_complete"),
    path("help/", views.HelpPage.as_view(), name="help_page"),
    path("", views.SiteHome.as_view(), name="site_home"),
]
