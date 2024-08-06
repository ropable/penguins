from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

admin.site.site_header = "Little Penguins Observations administration"
admin.site.index_title = "Little Penguins Observations"
admin.site.site_title = "Little Penguins Observations"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="logged_out.html"), name="logout"),
    #path("api/", include((API_URLS, "observations"), namespace="api")),
    path("", include("observations.urls")),
]
